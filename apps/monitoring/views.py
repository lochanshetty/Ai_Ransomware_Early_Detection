from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.monitoring.services import monitor_runtime


class MonitorStartAPIView(APIView):
    """Starts the monitoring runtime (phase-1 scaffold implementation)."""

    def post(self, request):
        run_id = monitor_runtime.start()
        return Response(
            {
                "message": "Monitoring started",
                "run_id": run_id,
                "status": monitor_runtime.status(),
            },
            status=status.HTTP_200_OK,
        )


class MonitorStatusAPIView(APIView):
    """Returns the current monitoring runtime state."""

    def get(self, request):
        return Response(monitor_runtime.status(), status=status.HTTP_200_OK)
