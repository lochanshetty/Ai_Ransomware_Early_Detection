import json
import os

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class CRDSEventConsumer(AsyncWebsocketConsumer):
    """Live security event stream for dashboard."""

    group_name = "crds_events"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"type": "connected", "message": "CRDS live stream active"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def crds_event(self, event):
        await self.send(text_data=json.dumps(event["payload"]))


async def broadcast_crds_event(payload: dict) -> None:
    """Broadcast event to all connected dashboard clients."""

    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    await channel_layer.group_send(
        "crds_events",
        {"type": "crds_event", "payload": payload},
    )
