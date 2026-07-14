from rest_framework.permissions import SAFE_METHODS, BasePermission


class CRDSPermission(BasePermission):
    """Authenticated by default; health/auth/schema remain public."""

    PUBLIC_PREFIXES = (
        '/healthz',
        '/api/auth/',
        '/api/schema',
        '/api/docs',
    )

    def has_permission(self, request, view):
        path = request.path
        if any(path.startswith(prefix) for prefix in self.PUBLIC_PREFIXES):
            return True
        if hasattr(view, 'permission_classes_override'):
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
