from django.urls import path
from . import views
app_name="statistics"
urlpatterns=[path("",views.overview,name="overview"),path("mitglied/<int:pk>/",views.member_detail,name="member")]
