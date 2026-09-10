from django.urls import path
from . import views
app_name="notifications"
urlpatterns=[
 path("",views.log_list,name="list"),
 path("einstellungen/",views.save_preferences,name="preferences"),
 path("push/subscribe/",views.subscribe,name="subscribe"),
 path("push/unsubscribe/",views.unsubscribe,name="unsubscribe"),
 path("push/test/",views.test_push,name="test_push"),
]
