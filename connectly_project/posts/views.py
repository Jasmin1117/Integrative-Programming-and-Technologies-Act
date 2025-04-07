from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory
from django.shortcuts import get_object_or_404
from .permissions import IsPostAuthor, IsPostAuthorOrAdmin, IsCommentAuthorOrAdmin
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.pagination import PageNumberPagination

# Get the user model
User = get_user_model()

# Initialize the logger for tracking events
logger = LoggerSingleton().get_logger()
logger.info("API initialized successfully.")


# --- Authentication and User Management ---


class ProtectedView(APIView):
    """Requires user to be logged in (authenticated) to access."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Authenticated request from user: {request.user.username}")
        return Response({"message": "Authenticated!"})


class UserListCreate(APIView):
    """Handles user registration and listing."""
    permission_classes = [AllowAny]  # Anyone can register

    def get(self, request):
        """Lists all registered users."""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Registers a new user."""
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")
        role = request.data.get("role", "User").capitalize()

        if not username or not password:
            logger.warning("User registration failed: Missing username or password.")
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            logger.warning(f"User registration failed: Username '{username}' already exists.")
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        if role == "Admin":
            user.is_staff = True
            user.role = "admin"
        elif role == "User":
            user.is_staff = False
            user.role = "user"
        else:
            user.is_staff = False
            user.role = "user"
            logger.warning(f"Invalid role provided: {role}. Defaulting to user.")
        user.save()

        logger.info(f"New user '{username}' registered successfully with role '{role}'.")
        serializer = UserSerializer(user)
        return Response({
            "message": "User created successfully.",
            "user": serializer.data,
        }, status=status.HTTP_201_CREATED)


class UserLogin(APIView):
    """Handles user login and token generation."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticates a user and generates a token."""
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            logger.info(f"User '{username}' logged in successfully.")
            return Response({"message": "Login successful.", "token": token.key}, status=status.HTTP_200_OK)

        logger.warning(f"Failed login attempt for user '{username}'.")
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


# --- Pagination ---


class PostPagination(PageNumberPagination):
    """Handles post pagination settings."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentPagination(PageNumberPagination):
    """Handles comment pagination settings."""
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20


# --- Post Management ---


class PostListCreate(APIView):
    """Handles listing and creating posts."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieves all posts."""
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)

        logger.info(f"User '{request.user.username}' retrieved all posts.")  # Add this log
        return Response(serializer.data)

    def post(self, request):
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

            serializer = PostSerializer(post)  # Serialize response
            logger.info(f"User '{request.user.username}' created a new {data['post_type']} post.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.warning(f"Post creation failed for user '{request.user.username}': {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """Handles viewing, updating, and deleting individual posts."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Retrieves a specific post."""
        try:
            post = get_object_or_404(Post, pk=pk)
            if post.privacy == 'private' and post.created_by != request.user:
                return Response({"error": "Privacy is private."}, status=status.HTTP_403_FORBIDDEN)
            return Response(PostSerializer(post).data)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        """Updates a specific post (only author can update)."""
        try:
            post = get_object_or_404(Post, pk=pk)
            if not IsPostAuthor().has_object_permission(request, self, post):  # changed here.
                return Response({'detail': 'You do not have permission to perform this action.'},
                                status=status.HTTP_403_FORBIDDEN)

            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User '{request.user.username}' edited post ID {pk}.")
                return Response(serializer.data)

            logger.error(f"Post update failed for user '{request.user.username}': {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """Deletes a specific post (only author or admin can delete)."""
        try:
            post = get_object_or_404(Post, pk=pk)
            if not IsPostAuthorOrAdmin().has_object_permission(request, self, post):
                return Response({'detail': 'You do not have permission to perform this action.'},
                                status=status.HTTP_403_FORBIDDEN)

            post.delete()
            logger.info(f"User '{request.user.username}' deleted post ID {pk}.")
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)


class NewsFeedView(ListAPIView):
    """Handles retrieving the news feed with pagination and filtering."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        """Retrieves posts for the news feed. (Public and private posts by the author)."""
        # Don't cache the queryset itself, just build it properly
        try:
            if self.request.user.role == 'guest':
                queryset = Post.objects.filter(privacy='public')
                logger.info(f"Guest user '{self.request.user.username}' fetching public posts.")
            else:
                queryset = Post.objects.filter(privacy='public') | Post.objects.filter(created_by=self.request.user)
                logger.info(f"Authenticated user '{self.request.user.username}' fetching their posts.")
        except Exception as e:
            logger.error(f"Error retrieving posts: {str(e)}")
            queryset = Post.objects.filter(privacy='public')

        # Handle liked-only filtering
        liked_only = self.request.query_params.get('liked_only')
        if liked_only and liked_only.lower() == 'true':
            liked_posts = Like.objects.filter(user=self.request.user).values_list('post_id', flat=True)
            queryset = queryset.filter(id__in=liked_posts)
            logger.info(f"User '{self.request.user.username}' requested liked-only posts.")

        # Sorting and prefetching comments
        queryset = queryset.order_by('-created_at').prefetch_related('comments')

        return queryset

    def list(self, request, *args, **kwargs):
        """Override list method to implement caching of the paginated, serialized response."""
        page = self.request.GET.get('page', 1)  # Default to page 1 if no page is provided
        liked_only = self.request.query_params.get('liked_only', 'false')

        # Create a cache key including relevant parameters
        cache_key = f"feed:{request.user.id}:{page}:liked_only={liked_only}"

        # Check if the cache exists for this key
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for {cache_key}.")
            return Response(cached_response)

        logger.info(f"Cache miss for {cache_key}. Fetching fresh data.")

        # Get the standard response from ListAPIView (which handles pagination)
        response = super().list(request, *args, **kwargs)

        # Cache the serialized and paginated response data
        cache.set(cache_key, response.data, timeout=60)  # Cache for 60 seconds
        logger.info(f"Cache set for {cache_key} with timeout of 60 seconds.")

        return response


# --- Comment Management ---


class CommentListCreate(APIView):
    """Handles creating comments on posts."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """Creates a comment on a specific post. """
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, post=post)  # Saves comment with post reference
            logger.info(f"User '{request.user.username}' added a comment to post {post_id}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Comment creation failed for user '{request.user.username}': {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDeleteView(DestroyAPIView):
    """Handles deleting comments."""
    permission_classes = [IsCommentAuthorOrAdmin]

    def delete(self, request, post_id, comment_id, *args, **kwargs):
        """Deletes a specific comment. (only author or admin can delete)"""
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class UserPostsView(APIView):
    """Handles retrieving posts created by the authenticated user."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieves posts created by the authenticated user."""
        posts = Post.objects.filter(created_by=request.user)
        serializer = PostSerializer(posts, many=True)
        logger.info(f"User '{request.user.username}' retrieved their posts.")
        return Response(serializer.data)


class OtherUserPostsView(APIView):
    """Handles retrieving posts created by another user."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None, username=None):
        """Retrieves posts created by a specific user (by ID or username)."""
        if user_id:
            user = get_object_or_404(User, id=user_id)
        elif username:
            user = get_object_or_404(User, username=username)
        else:
            return Response({"error": "User ID or Username is required"}, status=400)

        posts = Post.objects.filter(created_by=user)
        serializer = PostSerializer(posts, many=True)
        logger.info(f"User '{request.user.username}' retrieved posts of '{user.username}'.")
        return Response(serializer.data)


class PostCommentsView(ListAPIView):
    """Handles retrieving comments for a specific post with pagination."""
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieves comments for a specific post."""
        post_id = self.kwargs["post_id"]
        post = get_object_or_404(Post, id=post_id)
        logger.info(f"User '{self.request.user.username}' retrieved comments for post ID {post_id}.")
        return Comment.objects.filter(post=post)


# --- Like Management ---


class LikePostView(APIView):
    """Handles liking a post."""
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """Likes a specific post."""
        post = get_object_or_404(Post, id=post_id)

        if Like.objects.filter(user=request.user, post=post).exists():
            logger.info(f"User {request.user.username} tried to like post {post_id} again.")
            return Response({"error": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like = Like.objects.create(user=request.user, post=post)
        logger.info(f"User {request.user.username} liked post {post_id}.")

        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnlikePostView(APIView):
    """Handles unliking a post."""

    def delete(self, request, post_id):
        """Unlikes a specific post."""
        user = request.user
        post = get_object_or_404(Post, id=post_id)

        like = Like.objects.filter(user=user, post=post).first()
        if like:
            like.delete()
            return Response({"message": "Post unliked successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You haven't liked this post yet."}, status=status.HTTP_400_BAD_REQUEST)


from django.core.cache import cache
from urllib.parse import urlencode


def cache_with_query(timeout):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            query_string = urlencode(request.GET)
            key = f"custom_cache::{request.path}?{query_string}"
            response = cache.get(key)
            if response is None:
                response = view_func(request, *args, **kwargs)
                cache.set(key, response, timeout)
            return response

        return _wrapped_view

    return decorator


from django.core.cache import cache
from django.http import JsonResponse
from django.views import View


class HelloWorldView(View):
    """A simple view to demonstrate caching"""

    def get(self, request, *args, **kwargs):
        """Handles GET requests and caches the response"""
        cache_key = 'hello_world_response'

        # Check if the cached response exists
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit inner: {cache_key}")
            return JsonResponse({'message': 'Hello, World! (from cache)'})
        # If no cached response, set a new one
        cache.set(cache_key, 'Hello, World!', timeout=60)
        logger.info(f"Cache hit outer: {cache_key}")
        return JsonResponse({'message': 'Hello, World! (first time)'})
