from django.urls import path
from . import views
app_name="activities"
urlpatterns=[
 path("",views.activity_list,name="list"), path("kalender/",views.activity_calendar,name="calendar"),
 path("import/",views.activity_import,name="import"), path("import/bestaetigen/",views.activity_import_confirm,name="import_confirm"),
 path("standardzeiten/", views.activity_type_defaults, name="type_defaults"),
 path("neu/",views.activity_create,name="create"), path("<int:pk>/bearbeiten/",views.activity_update,name="update"), path("<int:pk>/loeschen/",views.activity_delete,name="delete"),
 path("<int:pk>/anwesenheit/",views.attendance,name="attendance"), path("<int:pk>/anwesenheit/<int:attendance_pk>/",views.attendance_update,name="attendance_update"),
 path("<int:pk>/betreuer-anwesenheit/<int:attendance_pk>/",views.supervisor_attendance_update,name="supervisor_attendance_update"),
 path("<int:pk>/anwesenheit/alle/",views.attendance_bulk,name="attendance_bulk"),
 path("<int:pk>/betreuer-anwesenheit/alle/",views.supervisor_attendance_bulk,name="supervisor_attendance_bulk"), path("<int:pk>/anwesenheit/abschliessen/",views.attendance_complete,name="attendance_complete"),]
