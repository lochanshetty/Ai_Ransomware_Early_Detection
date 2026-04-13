from rest_framework import serializers

from apps.detection.models import Alert


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
