"""Audit logging middleware for sensitive API operations."""

from apps.detection.models import AuditLog


class AuditLogMiddleware:
    SENSITIVE_PREFIXES = (
        '/system/',
        '/monitor/',
        '/honeypot/',
        '/demo/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and path.startswith(self.SENSITIVE_PREFIXES):
            user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            AuditLog.objects.create(
                user=user,
                action=f"{request.method} {path}",
                path=path,
                method=request.method,
                status_code=response.status_code,
                ip_address=self._client_ip(request),
                payload={'query': dict(request.GET)},
            )
        return response

    @staticmethod
    def _client_ip(request) -> str | None:
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
