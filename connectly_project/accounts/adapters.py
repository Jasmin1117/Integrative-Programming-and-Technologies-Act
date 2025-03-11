from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user

        logger.debug(f"Social login attempt: {user.email}")

        if not user.email:
            logger.error("No email provided in social login")
            return  # Do nothing if there's no email

        try:
            # Check if user already exists before modifying the role
            existing_user = User.objects.get(email=user.email)
            logger.info(f"User {user.email} exists. Linking account...")
            sociallogin.connect(request, existing_user)  # Link social account to existing user
        except User.DoesNotExist:
            logger.warning(f"User {user.email} does not exist. Creating a new user.")

            email_domain = user.email.split('@')[-1]

            if email_domain == "mmdc.mcl.edu.ph" or user.email in [
                'admin@example.com',
                'owner@example.com',
            ]:
                user.role = 'admin'
            else:
                user.role = 'user'

            user.save()
            logger.info(f"User {user.email} assigned role: {user.role}")