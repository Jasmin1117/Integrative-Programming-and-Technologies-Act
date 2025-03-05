from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user

        if user.email:
            # Automatically set admin role for certain emails
            if user.email in ['admin@example.com', 'owner@example.com', 'lr.jabejo@mmdc.mcl.edu.ph']:
                user.role = 'admin'
            else:
                user.role = 'user'
            user.save()
