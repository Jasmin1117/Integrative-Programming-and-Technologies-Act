from django.urls import path, include


from django.contrib.auth import views as auth_views

import accounts
from accounts.views import accounts_home

urlpatterns = [
    path('home/', accounts_home, name='accounts_home'),
    path('manage-users/', accounts.views.manage_users, name='manage_users'),
    path('admin-dashboard/', accounts.views.accounts_home, name='admin_dashboard'),
    path('login/', accounts.views.CustomLoginView.as_view(), name='login'),
    path('register/', accounts.views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('/', include('allauth.urls')),  # Allauth handles login/logout
]
