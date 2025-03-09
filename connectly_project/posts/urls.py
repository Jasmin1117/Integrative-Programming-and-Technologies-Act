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
    OtherUserPostsView,
    LikePostView,
    UnlikePostView,
    NewsFeedView,
    
)

urlpatterns = [
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentListCreate.as_view(), name='comment-list-create'),     
    path('user/posts/', UserPostsView.as_view(), name='user-posts'),
    path('post/<int:post_id>/comments/', PostCommentsView.as_view(), name='post-comments'),
    path('users/<int:user_id>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-id'),
    path('users/<str:username>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-username'),
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like_post'),
    path('posts/<int:post_id>/unlike/', UnlikePostView.as_view(), name='unlike-post'),
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
    
]


"""
- user can create account        : path('users/', UserListCreate.as_view(), name='user-list-create')
- user can login                 : path('login/', UserLogin.as_view(), name='user-login'),
- user can verify its token      : path('protected/', ProtectedView.as_view(), name='protected'),
- user can retrieve all users    : path('users/', UserListCreate.as_view(), name='user-list-create'),


- user can create post                                                          : path('posts/', PostListCreate.as_view(), name='post-list-create'),
- user can retrieve its own post (authenticated)                                : path('user/posts/', UserPostsView.as_view(), name='user-posts'),
- user can retrieve ALL posts                                                   : path('posts/', PostListCreate.as_view(), name='post-list-create'),
- user can retrieve  ALL post of a specific user (through user id / username)   : path('users/<int:user_id>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-id')   //////and/////   path('users/<str:username>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-username')
- user can edit its own post                                                    : path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail')
- user can delete its own post                                                  : path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail')


- user can create a comment (through post_id)        : path('posts/<int:post_id>/comments/', CommentListCreate.as_view(), name='comment-list-create'),  
- user can retrieve ALL comment of a specific post   : path('post/<int:post_id>/comments/', PostCommentsView.as_view(), name='post-comments'),
note: example to test comments with pagination ( https://127.0.0.1:8000/posts/post/1/comments/?page=1 ) add ?page=(number of page)


- user can like a post           :  path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like_post')
- user can unlike a post         :  path('posts/<int:post_id>/unlike/', UnlikePostView.as_view(), name='unlike-post')

- retrieve newsfeed newest first   : path('feed/', NewsFeedView.as_view(), name='news-feed')






- user can get specific post of a specific user      
- user can delete comments on its own post
- user can edit its own comment
- user can like a comment
- user can retrieve who like their post



"""