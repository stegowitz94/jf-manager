from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("profil/", views.profile, name="profile"),
    path("passwort-aendern/", views.password_change, name="password_change"),
]
