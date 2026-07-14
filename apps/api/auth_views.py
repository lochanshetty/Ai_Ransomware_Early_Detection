from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.models import User

from apps.api.serializers import RegisterSerializer


class RegisterAPIView(generics.CreateAPIView):
    """Register operator account for dashboard access."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginAPIView(TokenObtainPairView):
    """JWT login endpoint."""

    permission_classes = [permissions.AllowAny]


class MeAPIView(APIView):
    """Returns authenticated user profile."""

    def get(self, request):
        user = request.user
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
            }
        )
