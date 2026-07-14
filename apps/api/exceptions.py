"""Custom DRF exception handler."""

from rest_framework.views import exception_handler


def crds_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            'status': 'error',
            'detail': response.data,
        }
    return response
