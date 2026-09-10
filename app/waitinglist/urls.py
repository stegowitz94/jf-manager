from django.urls import path
from . import views
app_name="waitinglist"
urlpatterns=[path("",views.entry_list,name="list"),path("neu/",views.entry_create,name="create"),path("export/",views.export_xlsx,name="export"),path("<int:pk>/",views.entry_detail,name="detail"),path("<int:pk>/bearbeiten/",views.entry_update,name="update"),path("<int:pk>/uebernehmen/",views.convert_to_member,name="convert")]
