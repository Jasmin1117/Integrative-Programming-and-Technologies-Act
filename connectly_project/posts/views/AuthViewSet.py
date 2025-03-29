from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status


class AuthViewSet(ViewSet):
    permission_classes = [AllowAny]  # Allow login without authentication

    def login(self, request):
        """Authenticate user and return Token."""
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})

        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


    def logout(self, request):
        """Delete the user's token to log them out."""
        try:
            request.user.auth_token.delete()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except AttributeError:  # If user has no token
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
