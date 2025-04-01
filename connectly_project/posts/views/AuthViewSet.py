# posts/views/AuthViewSet.py
from rest_framework import viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import render


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]  # Allow login without authentication

    @action(detail=False, methods=['post'], url_path='login', url_name='login_post')
    def login(self, request):
        """Authenticate user and return Token along with a redirect URL."""
        username = request.data.get("username")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user:
            # Generate or retrieve the token for the user
            token, created = Token.objects.get_or_create(user=user)

            redirect_url = request.data.get('redirect_url', '/')

            return Response({
                "token": token.key,
                "redirect_url": redirect_url
            })

        # If authentication fails, return an error
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], url_path='logout', url_name='logout')
    def logout(self, request):
        """Delete the user's token to log them out."""
        try:
            if request.user.auth_token.key is None:
                return Response({"error": "Invalid Token"}, status=status.HTTP_403_FORBIDDEN)
            elif request.user.auth_token.key:
                request.user.auth_token.delete()
                return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except AttributeError:  # If user has no token
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
