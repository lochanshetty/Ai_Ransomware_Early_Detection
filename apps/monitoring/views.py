from pathlib import Path
import subprocess
import sys

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.detection.models import SecurityLog
from apps.monitoring.models import ProtectedFile
from apps.monitoring.services import monitor_runtime
from utils.encryption import decrypt_file


class MonitorStartAPIView(APIView):
    """Starts the monitoring runtime (phase-1 scaffold implementation)."""

    def post(self, request):
        monitor_runtime.start()
        print("[MONITOR] Monitoring started")
        return Response({"status": "running"}, status=status.HTTP_200_OK)


class MonitorStatusAPIView(APIView):
    """Returns the current monitoring runtime state."""

    def get(self, request):
        return Response(monitor_runtime.status(), status=status.HTTP_200_OK)


class MonitorLogsAPIView(APIView):
    """Returns latest file monitoring logs for demo verification."""

    def get(self, request):
        status_filter = str(request.query_params.get("status", "all")).lower()
        latest_logs = SecurityLog.objects.order_by("-created_at")
        if status_filter != "all":
            action_filters = {
                "success": ["create"],
                "warning": ["modify"],
                "alert": ["rename"],
                "blocked": ["rename", "delete"],
            }
            actions = action_filters.get(status_filter)
            if actions:
                latest_logs = latest_logs.filter(action__in=actions)
        latest_logs = latest_logs[:100]

        def _status_for(row: SecurityLog) -> str:
            if row.action in {"rename", "delete"}:
                return "blocked" if row.action == "delete" else "alert"
            if row.action == "modify":
                return "warning"
            return "success"

        data = [
            {
                "id": row.id,
                "source": row.source,
                "event_type": row.event_type,
                "action": row.action,
                "status": _status_for(row),
                "file_path": row.file_path,
                "message": row.message,
                "metadata": row.metadata,
                "timestamp": row.created_at.isoformat(),
            }
            for row in latest_logs
        ]
        return Response({"status": "ok", "results": data}, status=status.HTTP_200_OK)


class FileOpenAPIView(APIView):
    """Returns safe URL for opening monitored files in a new tab."""

    def get(self, request):
        requested_path = request.query_params.get("path")
        if not requested_path:
            return Response({"detail": "path is required"}, status=status.HTTP_400_BAD_REQUEST)

        resolved = str(Path(requested_path).resolve())
        preview_url = f"/file/view?path={resolved}"
        return Response({"status": "ok", "path": resolved, "preview_url": preview_url}, status=status.HTTP_200_OK)


class FileViewAPIView(APIView):
    """Renders monitored file content in plain text for quick inspection."""

    def get(self, request):
        requested_path = request.query_params.get("path")
        if not requested_path:
            return Response({"detail": "path is required"}, status=status.HTTP_400_BAD_REQUEST)

        path = Path(requested_path).resolve()
        if not path.exists() or not path.is_file():
            return Response({"detail": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        # Restrict preview to demo_files for safe demos.
        demo_root = Path(__file__).resolve().parents[2] / "demo_files"
        if not str(path).startswith(str(demo_root.resolve())):
            return Response({"detail": "Access denied for this path"}, status=status.HTTP_403_FORBIDDEN)

        content = path.read_text(encoding="utf-8", errors="replace")
        return HttpResponse(content, content_type="text/plain; charset=utf-8")


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
                decrypt_file(str(locked_file))

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
