from django.urls import path
from .views import (
    ProtectedView,
    UserListCreate,
    UserLogin,
    PostListCreate,
    PostDetailView,
    CommentListCreate
)

urlpatterns = [
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
]
