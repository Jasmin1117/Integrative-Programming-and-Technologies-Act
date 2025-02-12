from django.urls import path
from .views import (
    ProtectedView,
    UserListCreate,
    UserLogin,
    PostListCreate,
    PostDetailView,
    CommentListCreate,
    UserPostsView,
    PostCommentsView,
    OtherUserPostsView
)

urlpatterns = [
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('user/posts/', UserPostsView.as_view(), name='user-posts'),
    path('post/<int:post_id>/comments/', PostCommentsView.as_view(), name='post-comments'),
    path('users/<int:user_id>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-id'),
    path('users/<str:username>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-username'),
]
