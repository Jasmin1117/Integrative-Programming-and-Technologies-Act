from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import logging

from factories.post_factory import PostFactory
from posts.models import Post
from posts.serializers import PostSerializer, CommentSerializer

logger = logging.getLogger(__name__)


class PostWriteViewSet(viewsets.ModelViewSet):
    """Handles creating, updating, and deleting posts."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Creates a new post."""
        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {}),
                created_by=request.user,
                privacy=data.get('privacy', 'public')
            )
            serializer = self.get_serializer(post)
            logger.info(f"User '{request.user.username}' created a new {data['post_type']} post.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.warning(f"Post creation failed for user '{request.user.username}': {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Allow only the post owner to update the post."""
        post = self.get_object()
        if post.created_by != request.user:
            return Response({'detail': 'You do not have permission to update this post.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Allow only the post owner to delete the post."""
        post = self.get_object()
        if post.created_by != request.user:
            return Response({'detail': 'You do not have permission to delete this post.'},
                            status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({'message': 'Post deleted successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='comment', url_name='comment')
    def create_comment(self, request, pk=None):
        logger.info(f"Received request to create comment for post {pk}")
        post = get_object_or_404(Post, id=pk)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            logger.info(f"User '{request.user.username}' added a comment to post {pk}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Comment creation failed for user '{request.user.username}': {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
