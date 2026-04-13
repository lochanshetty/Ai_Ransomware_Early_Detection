from django.urls import path

from apps.dashboard.views import alerts_view, dashboard_home, logs_view

urlpatterns = [
    path("", dashboard_home, name="dashboard-home"),
    path("logs/", logs_view, name="dashboard-logs"),
    path("alerts/", alerts_view, name="dashboard-alerts"),
]
