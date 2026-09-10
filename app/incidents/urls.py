from django.urls import path

from . import views

app_name = "incidents"
urlpatterns = [
    path("", views.incident_list, name="list"),
    path("neu/", views.create_choice, name="create"),
    path("neu/vorfall/", views.incident_create, name="create_incident"),
    path("neu/unfall/", views.accident_create, name="create_accident"),
    path("<int:pk>/", views.incident_detail, name="detail"),
    path("<int:pk>/bearbeiten/", views.incident_update, name="update"),
    path("<int:pk>/archivieren/", views.incident_archive, name="archive"),
    path("<int:pk>/wehrfuehrung-melden/", views.notify_command, name="notify_command"),
]
