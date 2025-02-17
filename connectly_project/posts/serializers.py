from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Comment

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

    class Meta:
        model = Post
        fields = ["id", "title", "post_type", "content", "metadata", "author_id", "author_username", "created_at"]

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

# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)  # User ID
    author_username = serializers.CharField(source="user.username", read_only=True)  # Username
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_id', 'author_username', 'post', 'created_at']

    def validate_text(self, value):
        """Ensure comment text is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Comment text cannot be empty.")
        return value

    def validate_post(self, value):
        """Ensure the referenced post exists"""
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value
