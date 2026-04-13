from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deception.models import HoneypotFile
from apps.deception.services.honeypot_generator import create_honeypot_files
from apps.deception.services.honeypot_monitor import process_security_log
from apps.detection.models import SecurityLog


class HoneypotCreateAPIView(APIView):
    """Creates fake sensitive honeypot files in monitored directories."""

    def post(self, request):
        monitored_directories = request.data.get("monitored_directories", [])
        count = int(request.data.get("count", 5))
        files = create_honeypot_files(monitored_directories=monitored_directories, count=count)
        return Response(
            {
                "created_count": len(files),
                "files": [item.file_path for item in files],
            },
            status=status.HTTP_201_CREATED,
        )


class HoneypotStatusAPIView(APIView):
    """Returns current honeypot inventory status."""

    def get(self, request):
        total = HoneypotFile.objects.count()
        triggered = HoneypotFile.objects.filter(is_triggered=True).count()
        return Response(
            {
                "total_files": total,
                "triggered_files": triggered,
                "safe_files": max(total - triggered, 0),
            },
            status=status.HTTP_200_OK,
        )


class HoneypotTriggeredAPIView(APIView):
    """Lists honeypot files that were triggered by suspicious access."""

    def get(self, request):
        data = HoneypotFile.objects.filter(is_triggered=True).values("id", "file_path", "created_at")
        return Response({"triggered": list(data)}, status=status.HTTP_200_OK)


class HoneypotAccessReportAPIView(APIView):
    """Ingests monitoring events and forwards hits to detection pipeline."""

    def post(self, request):
        file_path = request.data.get("file_path")
        if not file_path:
            return Response(
                {"detail": "file_path is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_type = request.data.get("event_type", "file_access")
        process_name = request.data.get("process_name", "unknown")
        log = SecurityLog.objects.create(
            source="deception",
            event_type=event_type,
            message=f"File access event on {file_path}",
            metadata={
                "file_path": file_path,
                "process_name": process_name,
                "process_known": request.data.get("process_known", False),
                "files_accessed_count": request.data.get("files_accessed_count", 1),
            },
        )
        monitor_result = process_security_log(log)

        return Response(
            {
                "security_log_id": log.id,
                "message": "Access event recorded",
                "honeypot_triggered": monitor_result["triggered"],
                "threat_id": monitor_result["threat_id"],
            },
            status=status.HTTP_201_CREATED,
        )
