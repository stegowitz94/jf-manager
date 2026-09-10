from django.urls import path

from . import backup_views, views

app_name = "core"

urlpatterns = [
    path("setup/", views.setup_wizard, name="setup"),
    path("setup/wiederherstellen/", views.setup_restore, name="setup_restore"),
    path("service-worker.js", views.service_worker, name="service_worker"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("offline/", views.offline, name="offline"),
    path("", views.dashboard, name="dashboard"),
    path("dashboard/einstellungen/", views.dashboard_settings, name="dashboard_settings"),
    path("dashboard/layout-speichern/", views.dashboard_layout_save, name="dashboard_layout_save"),
    path("ui/tabelle/<str:table_key>/", views.table_preference_api, name="table_preference_api"),
    path("suche/api/", views.global_search_api, name="search_api"),
    path("health/", views.health, name="health"),
    path("suche/", views.global_search, name="search"),
    path("systemstatus/", views.system_status, name="system_status"),
    path("systemstatus/testmail/", views.send_test_email, name="send_test_email"),
    path("system/backup/", backup_views.backup_center, name="backup_center"),
    path("system/backup/download/", backup_views.backup_download, name="backup_download"),
    path("system/backup/wiederherstellen/", backup_views.backup_restore, name="backup_restore"),
    path("system/backup/sicherheit/<str:filename>/", backup_views.safety_backup_download, name="safety_backup_download"),
]
