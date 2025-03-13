from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import JsonResponse

User = get_user_model()
from django.contrib.auth import authenticate
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
from .permissions import IsPostAuthor, IsAuthorOrAdmin
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.pagination import PageNumberPagination



# Initialize Logger
logger = LoggerSingleton().get_logger()
logger.info("API initialized successfully.")

# Require Authentication for All Endpoints
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Authenticated request from user: {request.user.username}")
        return Response({"message": "Authenticated!"})


# User Registration
class UserListCreate(APIView):
    permission_classes = [AllowAny]


    # Retrieves a list of all registered users.
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # Registers a new user with a username, password, email, and role
    def post(self, request):
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
        elif role== "User":   
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


# User Login
class UserLogin(APIView):
    permission_classes = [AllowAny]

    # Authenticates a user and generates a token
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            logger.info(f"User '{username}' logged in successfully.")
            return Response({"message": "Login successful.", "token": token.key}, status=status.HTTP_200_OK)
        
        logger.warning(f"Failed login attempt for user '{username}'.")
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


# Post Management
class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Retrieves all posts from the database
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        
        logger.info(f"User '{request.user.username}' retrieved all posts.")  # Add this log
        return Response(serializer.data)
    
    # Creates a new post using PostFactory
    def post(self, request):
        data = request.data  
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {}),
                created_by=request.user  # Ensure created_by is passed
            )
            
            serializer = PostSerializer(post)  # Serialize response
            logger.info(f"User '{request.user.username}' created a new {data['post_type']} post.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.warning(f"Post creation failed for user '{request.user.username}': {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrAdmin]

    def get(self, request, pk):
        try:
            post = get_object_or_404(Post, pk=pk)
            self.check_object_permissions(request, post)

            return Response(PostSerializer(post).data)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        

    def put(self, request, pk):
        try:
            post = get_object_or_404(Post, pk=pk)
            self.check_object_permissions(request, post)
            
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
        try:
            post = get_object_or_404(Post, pk=pk)
            self.check_object_permissions(request, post)
            
            post.delete()
            logger.info(f"User '{request.user.username}' deleted post ID {pk}.")
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)


# Comment Management
class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Creates a new comment
    def post(self, request, post_id):  # <-- Extracts post_id from URL
        post = get_object_or_404(Post, id=post_id)  # Ensures post exists
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, post=post)  # Saves comment with post reference
            logger.info(f"User '{request.user.username}' added a comment to post {post_id}.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Comment creation failed for user '{request.user.username}': {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDeleteView(DestroyAPIView):
    permission_classes = [IsAuthorOrAdmin]

    def delete(self, request, post_id, comment_id, *args, **kwargs):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        self.check_object_permissions(request, comment) 
        comment.delete()
        return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class UserPostsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Retrieve posts by the authenticated user
    def get(self, request):
        posts = Post.objects.filter(created_by=request.user)
        serializer = PostSerializer(posts, many=True)
        logger.info(f"User '{request.user.username}' retrieved their posts.")
        return Response(serializer.data)


class OtherUserPostsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Retrieve posts by another user (specified via user_id or username)
    def get(self, request, user_id=None, username=None):
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


class CommentPagination(PageNumberPagination):
    page_size = 5  # Default 5 comments per page
    page_size_query_param = "page_size"
    max_page_size = 20


class PostCommentsView(ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # retrieve comments per post
    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        post = get_object_or_404(Post, id=post_id)  # Ensure post exists
        logger.info(f"User '{self.request.user.username}' retrieved comments for post ID {post_id}.")
        return Comment.objects.filter(post=post)


class LikePostView(APIView):
    permission_classes = [IsAuthenticated]  

    # like a post
    def post(self, request, post_id):
        # Get the post object
        post = get_object_or_404(Post, id=post_id)

        if Like.objects.filter(user=request.user, post=post).exists():
            logger.info(f"User {request.user.username} tried to like post {post_id} again.")
            return Response({"error": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like = Like.objects.create(user=request.user, post=post)
        logger.info(f"User {request.user.username} liked post {post_id}.")
        
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class UnlikePostView(APIView):

    # unlike a post
    def delete(self, request, post_id):
        user = request.user  # Get the authenticated user
        post = get_object_or_404(Post, id=post_id)  # Ensure the post exists

        like = Like.objects.filter(user=user, post=post).first()  # Find existing like
        if like:
            like.delete()  # Remove the like
            return Response({"message": "Post unliked successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You haven't liked this post yet."}, status=status.HTTP_400_BAD_REQUEST)


class PostPagination(PageNumberPagination):
    page_size = 10  # Number of posts per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class NewsFeedView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        logger.info(f"User '{self.request.user.username}' accessed the news feed.")

        # Restrict guest users to only public posts
        try:
            if self.request.user.role == 'guest':
                queryset = Post.objects.filter(privacy='public')
                logger.info(f"Guest user '{self.request.user.username}' can only see public posts.")
            else:
                queryset = Post.objects.filter(privacy='public') | Post.objects.filter(user=self.request.user)
        except:
            queryset = Post.objects.filter(privacy='public')

        # Sorting and prefetching comments
        queryset = queryset.order_by('-created_at').prefetch_related('comments')

        # Handle liked-only filtering
        liked_only = self.request.query_params.get('liked_only')
        if liked_only and liked_only.lower() == 'true':
            liked_posts = Like.objects.filter(user=self.request.user).values_list('post_id', flat=True)
            queryset = queryset.filter(id__in=liked_posts)
            logger.info(f"User '{self.request.user.username}' requested liked-only posts.")
            if not queryset.exists():
                logger.info(f"User '{self.request.user.username}' has no liked posts.")
        return queryset
    



"""
test if
admin can delete other posts
admin can delete other comments

user cannot delete other posts
user cannot delete other comments



"""