from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Comment, Like

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Exclude sensitive fields like password

    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

# Post Serializer
class PostSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source="created_by", read_only=True)  
    author_username = serializers.CharField(source="created_by.username", read_only=True)  
    like_count = serializers.SerializerMethodField() 
    comment_count = serializers.SerializerMethodField() 

    class Meta:
        model = Post
        fields = ["id", "title", "content", "author_id", "author_username", "post_type", "metadata", "created_at", "like_count", "comment_count"]


    def validate_title(self, value):
        """Ensure title is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_content(self, value):
        """Ensure content is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value

    def validate_post_type(self, value):
        """Ensure post_type is either 'text', 'image', or 'video'"""
        if value not in ["text", "image", "video"]:
            raise serializers.ValidationError("Invalid post type. Must be 'text', 'image', or 'video'.")
        return value
    
    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(source="text")  # Rename text to comment
    author_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)
    author_username = serializers.CharField(source="user.username", read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(source="post.id", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'comment', 'post_id', 'author_id', 'author_username', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_comment(self, value):  # Update validation method
        """Ensure comment is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Comment cannot be empty.")
        return value


# Like Serializer
class LikeSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)  # User ID
    author_username = serializers.CharField(source="user.username", read_only=True)  # Username
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())  # Allow post selection

    class Meta:
        model = Like
        fields = ['author_id', 'author_username', 'post_id']

    def validate(self, data):
        """Ensure a user cannot like the same post more than once."""
        user = self.context['request'].user  # Get the authenticated user
        post = data.get('post')

        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("You have already liked this post.")

        return data
