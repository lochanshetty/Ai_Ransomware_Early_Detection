from pathlib import Path
import subprocess
import sys

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.detection.models import SecurityLog
from apps.monitoring.models import ProtectedFile
from apps.monitoring.services import monitor_runtime


class MonitorStartAPIView(APIView):
    """Starts the monitoring runtime (phase-1 scaffold implementation)."""

    def post(self, request):
        monitor_runtime.start()
        return Response({"status": "Monitoring started"}, status=status.HTTP_200_OK)


class MonitorStatusAPIView(APIView):
    """Returns the current monitoring runtime state."""

    def get(self, request):
        return Response(monitor_runtime.status(), status=status.HTTP_200_OK)


class MonitorLogsAPIView(APIView):
    """Returns latest file monitoring logs for demo verification."""

    def get(self, request):
        latest_logs = SecurityLog.objects.order_by("-created_at")[:50]
        data = [
            {
                "id": row.id,
                "source": row.source,
                "event_type": row.event_type,
                "action": row.action,
                "file_path": row.file_path,
                "message": row.message,
                "metadata": row.metadata,
                "timestamp": row.created_at.isoformat(),
            }
            for row in latest_logs
        ]
        return Response({"results": data}, status=status.HTTP_200_OK)


class RegistryAddAPIView(APIView):
    """Adds a file path to the protected file registry."""

    def post(self, request):
        file_path = request.data.get("file_path")
        if not file_path:
            return Response({"detail": "file_path is required"}, status=status.HTTP_400_BAD_REQUEST)

        normalized = str(Path(file_path).resolve())
        file_type = Path(normalized).suffix.lower() or "unknown"
        row, _ = ProtectedFile.objects.get_or_create(
            file_path=normalized,
            defaults={"file_type": file_type},
        )
        if monitor_runtime.status().get("is_running"):
            # Rebuild watch targets so newly registered folders are monitored immediately.
            monitor_runtime.restart()
        return Response(
            {
                "id": row.id,
                "file_path": row.file_path,
                "file_type": row.file_type,
                "added_at": row.added_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class RegistryListAPIView(APIView):
    """Lists all protected files in registry."""

    def get(self, request):
        data = [
            {
                "id": row.id,
                "file_path": row.file_path,
                "file_type": row.file_type,
                "added_at": row.added_at.isoformat(),
            }
            for row in ProtectedFile.objects.order_by("-added_at")
        ]
        return Response({"results": data}, status=status.HTTP_200_OK)


class DemoRunAPIView(APIView):
    """Runs safe ransomware simulation and returns latest demo summary."""

    def post(self, request):
        base_dir = Path(__file__).resolve().parents[2]
        demo_dir = base_dir / "demo_files"
        simulate_script = base_dir / "simulate_attack.py"

        # Reset .locked files for repeatable demos.
        for locked_file in demo_dir.glob("*.locked"):
            original = locked_file.with_name(locked_file.name.replace(".locked", ""))
            if not original.exists():
                locked_file.rename(original)

        monitor_runtime.start()
        subprocess.run([sys.executable, str(simulate_script)], check=True)

        logs = SecurityLog.objects.order_by("-created_at")[:20]
        latest_logs = [
            {
                "id": row.id,
                "action": row.action,
                "file_path": row.file_path,
                "timestamp": row.created_at.isoformat(),
            }
            for row in logs
        ]
        return Response(
            {
                "status": "Demo attack completed",
                "log_count": len(latest_logs),
                "latest_logs": latest_logs,
            },
            status=status.HTTP_200_OK,
        )
