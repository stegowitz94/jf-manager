from django.urls import path
from . import views
app_name="documents"
urlpatterns=[
 path("",views.center,name="center"),path("betreuer.xlsx",views.supervisors_export,name="supervisors_export"),path("termine.xlsx",views.activities_export,name="activities_export"),path("anwesenheiten.xlsx",views.attendance_export,name="attendance_export"),
 path("kontaktliste.pdf",views.contact_pdf,name="contact_pdf"),path("geburtstage.pdf",views.birthdays_pdf,name="birthdays_pdf"),path("warteliste.pdf",views.waiting_pdf,name="waiting_pdf"),
]
