from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts import views

urlpatterns = [
    path('home/', views.accounts_home, name='accounts_home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('admin-posts/', views.admin_posts, name='admin_posts'),
    path('admin-comments/', views.admin_comments, name='admin_comments'),
    
    # API endpoints for user management
    path('api/users/<int:user_id>/', views.get_user_api, name='get_user_api'),
    path('api/users/<int:user_id>/update/', views.update_user_api, name='update_user_api'),
    path('api/users/<int:user_id>/deactivate/', views.deactivate_user_api, name='deactivate_user_api'),
    path('api/users/<int:user_id>/activate/', views.activate_user_api, name='activate_user_api'),
    path('api/users/<int:user_id>/delete/', views.delete_user_api, name='delete_user_api'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('/', include('allauth.urls')),  # Allauth handles login/logout
]
