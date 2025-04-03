from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from accounts.adapters import User
from posts.models import Post, Comment
from posts.serializers import PostSerializer, CommentSerializer, UserSerializer


class PostRegularUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Handles listing and retrieving posts with privacy checks."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override the default list() method to return only public posts.
    # This handles GET requests to /posts/ and ensures that only posts
    # with 'public' privacy are listed for any user.
    def list(self, request, *args, **kwargs):
        posts = Post.objects.filter(privacy='public')
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    # Retrieve a single post by ID with privacy checks.
    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        if post.privacy == 'private' and post.created_by != request.user:
            return Response({'detail': 'You do not have permission to view this post.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='public', permission_classes=[])
    def public_posts(self, request):
        """List all public posts (no auth required)."""
        posts = Post.objects.filter(privacy='public')
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='private')
    def private_posts(self, request):
        """List only the authenticated user's private posts."""
        posts = Post.objects.filter(privacy='private', created_by=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='comments')
    def get_comments(self, request, pk=None):
        """Retrieve all comments of a public post."""
        post = self.get_object()

        # Check if the post is public
        if post.privacy != 'public':
            return Response(
                {'detail': 'Comments are only visible for public posts.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all comments of this post
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='comments', name="get-post-comments", permission_classes=[IsAuthenticated])
    def get_post_comments(self, request, post_pk):
        """View to display all comments for a specific post."""
        post = get_object_or_404(Post, pk=post_pk)

        # Check if the post is public or belongs to the current user
        if post.privacy != 'public' and post.created_by != request.user:
            return HttpResponseForbidden("You don't have permission to view this post's comments.")

        comments = Comment.objects.filter(post=post).order_by('-created_at')

        context = {
            'post': post,
            'comments': comments,
        }

        return render(request, 'posts/post_comments.html', context)

    @action(detail=True, methods=['post'], url_path='comments', name="posts-regular-user-comments",
            permission_classes=[IsAuthenticated])
    def create_comment(self, request, pk=None):
        """Creates a comment on a specific post."""
        post = get_object_or_404(Post, id=pk)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # posts/posts/{pk}/countlikes/
    @action(detail=True, methods=['get'], url_path='countlikes')
    def count_likes(self, request, pk=None):
        """Retrieve the number of likes for a post."""
        post = self.get_object()
        return Response({'likes_count': post.likes.count()}, status=status.HTTP_200_OK)

    # posts/posts/{pk}/likedby/
    @action(detail=True, methods=['get'], url_path='likedby')
    def liked_by(self, request, pk=None):
        """Retrieve the list of users who liked a post."""
        post = self.get_object()

        if post.privacy != 'public':
            return Response()

        # Fetch users who liked the post (via the Like model)
        liked_users = User.objects.filter(likes__post=post)

        serializer = UserSerializer(liked_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
