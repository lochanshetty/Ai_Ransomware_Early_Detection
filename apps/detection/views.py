from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.detection.models import DetectedThreat


class DetectAnalyzeAPIView(APIView):
    """Phase-1 AI detection stub for anomaly scoring and threat logging."""

    def post(self, request):
        payload = request.data or {}
        anomaly_score = float(payload.get("anomaly_score", 0.35))
        is_threat = anomaly_score >= 0.7

        threat_record = None
        if is_threat:
            threat_record = DetectedThreat.objects.create(
                threat_name=payload.get("threat_name", "Potential ransomware activity"),
                confidence_score=anomaly_score,
                severity=payload.get("severity", "high"),
                analysis_payload=payload,
                is_confirmed=False,
            )

        return Response(
            {
                "anomaly_score": anomaly_score,
                "is_threat": is_threat,
                "threat_id": threat_record.id if threat_record else None,
            },
            status=status.HTTP_200_OK,
        )
