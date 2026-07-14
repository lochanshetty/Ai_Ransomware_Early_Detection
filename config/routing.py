from django.urls import path

from apps.api.consumers import CRDSEventConsumer

websocket_urlpatterns = [
    path("ws/events/", CRDSEventConsumer.as_asgi()),
]
