from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    POST_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )

    title = models.CharField(max_length=255)  # Add missing title field
    content = models.TextField(blank=True)  
    post_type = models.CharField(max_length=10, choices=POST_TYPES)  # Add post type
    metadata = models.JSONField(default=dict)  # Store metadata as JSON
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.created_by.username}"


# Comment Model
class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"