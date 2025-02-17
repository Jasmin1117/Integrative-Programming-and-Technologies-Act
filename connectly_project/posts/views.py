from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer # Custom permission
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory
from django.shortcuts import get_object_or_404
from .permissions import IsPostAuthor


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
        user.save()

        valid_roles = ["Admin", "User"]
        if role not in valid_roles:
            logger.warning(f"User '{username}' attempted to register with an invalid role: {role}")
            return Response({"error": "Invalid role. Choose 'Admin' or 'User'."}, status=status.HTTP_400_BAD_REQUEST)

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        logger.info(f"New user '{username}' registered successfully with role '{role}'.")
        return Response({
            "message": "User created successfully.",
            "role": role
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
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            return Response(PostSerializer(post).data)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            # No need to check if user is Admin or if the user is the author, IsPostAuthor does that
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
            post = Post.objects.get(pk=pk)
            # The IsPostAuthor permission will automatically check if the user is the author
            post.delete()
            logger.info(f"User '{request.user.username}' deleted post ID {pk}.")
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)


    # Deletes a post
    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)

            if request.user.groups.filter(name="Admin").exists() or post.created_by == request.user:
                post.delete()
                logger.info(f"User '{request.user.username}' deleted post ID {pk}.")
                return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            
            logger.warning(f"User '{request.user.username}' attempted to delete another user's post.")
            return Response({"error": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {pk} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)


# Comment Management
class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Retrieves all comments.
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)

        username = getattr(request.user, 'username', 'Anonymous')  # Handle unauthenticated users
        logger.info(f"User '{username}' retrieved all comments.")  # Log the request

        return Response(serializer.data)

    # Creates a new comment
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(f"User '{request.user.username}' added a new comment.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Comment creation failed for user '{request.user.username}': {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


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
    

class PostCommentsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Retrieve comments per post 
    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            logger.info(f"User '{request.user.username}' retrieved comments for post ID {post_id}.")
            return Response(serializer.data)
        except Post.DoesNotExist:
            logger.error(f"Post with ID {post_id} not found.")
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)




