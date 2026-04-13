from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deception.services.honeypot_manager import create_honeypot_files
from apps.detection.models import SecurityLog


class HoneypotSetupAPIView(APIView):
    """Creates fake sensitive files used as honeypots."""

    def post(self, request):
        base_dir = request.data.get("base_directory")
        files = create_honeypot_files(base_dir)
        return Response(
            {
                "created_count": len(files),
                "files": [item.file_path for item in files],
            },
            status=status.HTTP_201_CREATED,
        )


class HoneypotAccessReportAPIView(APIView):
    """
    Receives access events from monitors.

    Creating the SecurityLog automatically triggers deception detection signal.
    """

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

        return Response(
            {"security_log_id": log.id, "message": "Access event recorded"},
            status=status.HTTP_201_CREATED,
        )
