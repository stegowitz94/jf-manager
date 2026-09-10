from django.urls import path
from . import views
app_name='todos'
urlpatterns=[
    path('',views.todo_list,name='list'),
    path('neu/',views.todo_create,name='create'),
    path('<int:pk>/bearbeiten/',views.todo_update,name='update'),
    path('<int:pk>/erledigt/',views.todo_complete,name='complete'),
    path('<int:pk>/mitglied/<int:status_pk>/erledigt/',views.member_complete,name='member_complete'),
    path('<int:pk>/termin/<int:activity_pk>/anwesende-erledigt/',views.complete_present_members,name='complete_present_members'),
]
