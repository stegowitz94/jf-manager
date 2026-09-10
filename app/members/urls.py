from django.urls import path
from . import views

app_name = "members"
urlpatterns = [
    path("", views.member_list, name="list"),
    path("export/", views.member_export, name="export"),
    path("import/", views.member_import, name="import"),
    path("import/vorlage/", views.member_import_template, name="import_template"),
    path("pruefboegen/", views.member_check_sheets_bulk, name="check_sheets_bulk"),
    path("neu/", views.member_create, name="create"),
    path("<int:pk>/", views.member_detail, name="detail"),
    path("<int:pk>/bearbeiten/", views.member_update, name="update"),
    path("<int:pk>/pruefbogen/", views.member_check_sheet, name="check_sheet"),
    path("<int:member_pk>/abzeichen/neu/", views.badge_create, name="badge_create"),
    path("abzeichen/<int:pk>/bearbeiten/", views.badge_update, name="badge_update"),
    path("abzeichen/<int:pk>/loeschen/", views.badge_delete, name="badge_delete"),
    path("<int:member_pk>/beurlaubungen/neu/", views.leave_create, name="leave_create"),
    path("beurlaubungen/<int:pk>/bearbeiten/", views.leave_update, name="leave_update"),
]
