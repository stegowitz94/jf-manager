from django.urls import path

from .views import SupervisorCreateView, SupervisorDetailView, SupervisorListView, SupervisorUpdateView, training_create, training_update

app_name = "supervisors"
urlpatterns = [
    path("", SupervisorListView.as_view(), name="list"),
    path("neu/", SupervisorCreateView.as_view(), name="create"),
    path("<int:pk>/", SupervisorDetailView.as_view(), name="detail"),
    path("<int:pk>/bearbeiten/", SupervisorUpdateView.as_view(), name="update"),
    path("<int:pk>/fortbildungen/neu/", training_create, name="training_create"),
    path("<int:pk>/fortbildungen/<int:training_pk>/bearbeiten/", training_update, name="training_update"),
]
