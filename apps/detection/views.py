from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.detection.models import SecurityLog, Threat
from apps.detection.serializers import ThreatSerializer
from apps.detection.services.pipeline import analyze_log


class DetectAnalyzeAPIView(APIView):
    """Runs manual detection on a selected log or recent logs."""

    def post(self, request):
        log_id = request.data.get("security_log_id")

        if log_id:
            log = get_object_or_404(SecurityLog, id=log_id)
            result = analyze_log(log)
            return Response({"results": [result]}, status=status.HTTP_200_OK)

        # Fallback: analyze most recent logs manually when no ID is provided.
        logs = SecurityLog.objects.order_by("-created_at")[:20]
        results = [analyze_log(log) for log in logs]
        suspicious_count = len([item for item in results if item["is_suspicious"]])

        return Response(
            {
                "analyzed_logs": len(results),
                "suspicious_logs": suspicious_count,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class ThreatListAPIView(generics.ListAPIView):
    """Lists threats identified by automatic and manual detection flows."""

    queryset = Threat.objects.select_related("security_log").order_by("-detected_at")
    serializer_class = ThreatSerializer
