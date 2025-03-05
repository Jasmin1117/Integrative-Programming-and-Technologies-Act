from django.urls import path, include
from .views import admin_dashboard

urlpatterns = [
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('accounts/', include('allauth.urls')),  # Allauth handles login/logout
]
