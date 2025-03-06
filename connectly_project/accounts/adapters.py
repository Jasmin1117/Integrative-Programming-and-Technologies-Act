from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user

        if not user.email:
            return  # Do nothing if there's no email

        try:
            # Check if user already exists before modifying the role
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)  # Link social account to existing user
            return  # Exit early to prevent duplicate user creation
        except User.DoesNotExist:
            # New user, assign the role
            if user.email in ['admin@example.com', 'owner@example.com', 'lr.jabejo@mmdc.mcl.edu.ph', 'jomariabejo@gmail.com']:
                user.role = 'admin'
            else:
                user.role = 'user'
            user.save()
