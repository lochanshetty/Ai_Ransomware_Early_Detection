from django.contrib.auth.models import User
from rest_framework import permissions, serializers

from apps.detection.models import Alert


class AllowPublicPaths(permissions.BasePermission):
    """Allow unauthenticated access to health and auth endpoints."""

    def has_permission(self, request, view):
        public_paths = getattr(request, '_crds_public', None)
        from django.conf import settings
        public = settings.CRDS_PUBLIC_PATHS
        if request.path in public or request.path.rstrip('/') in public:
            return True
        return request.user and request.user.is_authenticated


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for alert records exposed by CRDS APIs."""

    class Meta:
        model = Alert
        fields = (
            "id",
            "title",
            "description",
            "status",
            "severity",
            "threat",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
