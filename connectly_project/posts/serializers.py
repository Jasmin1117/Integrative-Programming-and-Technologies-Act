from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Comment

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Exclude sensitive fields like password


# Post Serializer
class PostSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source="created_by", read_only=True)  
    author_username = serializers.CharField(source="created_by.username", read_only=True)  

    class Meta:
        model = Post
        fields = ["id", "title", "post_type", "content", "metadata", "author_id", "author_username", "created_at"]


# Comment Serializer (Fixed)
class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)  # User ID
    author_username = serializers.CharField(source="user.username", read_only=True)  # Username
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_id', 'author_username', 'post', 'created_at']

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value