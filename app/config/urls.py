from django.contrib import admin
from django.urls import include, path
from core.views import protected_media
urlpatterns = [
    path("admin/", admin.site.urls),
    path("media/<path:path>", protected_media, name="protected_media"),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("mitglieder/", include("members.urls")),
    path("termine/", include("activities.urls")),
    path("betreuer/", include("supervisors.urls")),
    path("vorfaelle/", include("incidents.urls")),
    path("todos/", include("todos.urls")),
    path("warteliste/", include("waitinglist.urls")),
    path("dokumente/", include("documents.urls")),
    path("audit/", include("audit.urls")),
    path("statistiken/", include("reports.urls")),
    path("benachrichtigungen/", include("notifications.urls")),
    path("", include("core.urls")),
]
