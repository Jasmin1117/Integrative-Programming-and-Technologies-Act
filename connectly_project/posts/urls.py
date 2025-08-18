from django.urls import path
from posts.views import (
    # Authentication & Users
    ProtectedView, UserListCreate,

    # Posts
    CreatePostView, EditPostView, DeletePostView, MyPostsView,
    PostDetailView, UserPostsView, OtherUserPostsView,
    NewsFeedView, LatestPostsView, PublicPostsView,

    # Post APIs
    PostRegularUser, PublicPosts, PrivatePosts,

    # Comments
    PostComments, PostCommentsView, CreateComment, CommentDeleteView,

    # Likes
    LikePostView, UnlikePostView, CountLikes, LikedBy, PostCommentsDetails,

    # Admin API Views
    AdminPostAPI, AdminPostUpdateAPI, AdminPostDeleteAPI,
    AdminCommentAPI, AdminCommentUpdateAPI, AdminCommentDeleteAPI,
)

urlpatterns = [
    # Authentication & User Management
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),

    # Post Management
    path('posts/', PostRegularUser.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/public/', PublicPosts.as_view(), name='public-posts'),
    path('posts/private/', PrivatePosts.as_view(), name='private-posts'),
    path('posts/create/', CreatePostView.as_view(), name='create_post'),
    path('posts/edit/<int:post_id>/', EditPostView.as_view(), name='edit_post'),
    path('posts/delete/<int:post_id>/', DeletePostView.as_view(), name='delete_post'),
    path('posts/my-posts/', MyPostsView.as_view(), name='my_posts'),
    path('posts/feed/', NewsFeedView.as_view(), name='news-feed'),
    path('posts/feed/latest/', LatestPostsView.as_view(), name='latest_posts'),
    path('posts/feed/public/', PublicPostsView.as_view(), name='public_posts'),

    # User-Specific Post Retrieval
    path('user/posts/', UserPostsView.as_view(), name='user-posts'),
    path('users/<int:user_id>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-id'),
    path('users/<str:username>/posts/', OtherUserPostsView.as_view(), name='other-user-posts-by-username'),

    # Comment Management
    path('posts/<int:post_pk>/comments/', PostCommentsDetails.as_view(), name='post-comments'),
    path('posts/<int:pk>/comments/create/', CreateComment.as_view(), name='create-comment'),
    path('posts/<int:pk>/comments/create/', CreateComment.as_view(), name='create-comment'),
    path('posts/<int:post_id>/comments/<int:comment_id>/delete/', CommentDeleteView.as_view(), name='comment-delete'),

    # Likes & Engagement
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like_post'),
    path('posts/<int:post_id>/unlike/', UnlikePostView.as_view(), name='unlike-post'),
    path('posts/<int:pk>/countlikes/', CountLikes.as_view(), name='count-likes'),
    path('posts/<int:pk>/likedby/', LikedBy.as_view(), name='liked-by'),

    # Admin API endpoints for post and comment management
    path('api/posts/<int:post_id>/', AdminPostAPI.as_view(), name='post-api-detail'),
    path('api/posts/<int:post_id>/update/', AdminPostUpdateAPI.as_view(), name='post-api-update'),
    path('api/posts/<int:post_id>/delete/', AdminPostDeleteAPI.as_view(), name='post-api-delete'),
    path('api/comments/<int:comment_id>/', AdminCommentAPI.as_view(), name='comment-api-detail'),
    path('api/comments/<int:comment_id>/update/', AdminCommentUpdateAPI.as_view(), name='comment-api-update'),
    path('api/comments/<int:comment_id>/delete/', AdminCommentDeleteAPI.as_view(), name='comment-api-delete'),
]

"""
API Documentation (Base URL: http://127.0.0.1:8000/posts)

User Management:
- Create Account: [POST] /users/
- Token Verification: [GET] /protected/

Posts:
- Create Post: [POST] /posts/create/
- Retrieve All Posts: [GET] /posts/
- Retrieve User's Posts: [GET] /user/posts/
- Retrieve Specific User's Posts: [GET] /users/<user_id>/posts/ or /users/<username>/posts/
- Retrieve Single Post: [GET] /posts/<pk>/
- Edit Post: [PUT] /posts/edit/<post_id>/
- Delete Post: [DELETE] /posts/delete/<post_id>/

Comments:
- Retrieve Comments for a Post: [GET] /posts/<post_id>/comments/
- Create Comment: [POST] /posts/<pk>/comments/create/
- Delete Comment: [DELETE] /posts/<post_id>/comments/<comment_id>/delete/

Likes:
- Like a Post: [POST] /posts/<post_id>/like/
- Unlike a Post: [POST] /posts/<post_id>/unlike/
- Count Post Likes: [GET] /posts/<pk>/countlikes/
- See Who Liked a Post: [GET] /posts/<pk>/likedby/

Newsfeed:
- Get Newsfeed: [GET] /posts/feed/
- Get Latest Posts: [GET] /posts/feed/latest/
- Get Public Posts: [GET] /posts/feed/public/

"""
