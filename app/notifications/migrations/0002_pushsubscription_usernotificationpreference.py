from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    dependencies=[("notifications","0001_initial"),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
      migrations.CreateModel(name="UserNotificationPreference",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("email_enabled",models.BooleanField(default=True,verbose_name="E-Mail")),("push_enabled",models.BooleanField(default=False,verbose_name="Push")),("birthdays",models.BooleanField(default=True,verbose_name="Geburtstage")),("absences",models.BooleanField(default=True,verbose_name="Fehlserien")),("leave_end",models.BooleanField(default=True,verbose_name="Beurlaubungsende")),("upcoming_activity",models.BooleanField(default=True,verbose_name="Nächster Termin")),("user",models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name="notification_preference",to=settings.AUTH_USER_MODEL))]),
      migrations.CreateModel(name="PushSubscription",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("endpoint",models.URLField(max_length=1000,unique=True)),("p256dh",models.TextField()),("auth",models.TextField()),("user_agent",models.CharField(blank=True,max_length=500)),("created_at",models.DateTimeField(auto_now_add=True)),("last_seen_at",models.DateTimeField(auto_now=True)),("user",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="push_subscriptions",to=settings.AUTH_USER_MODEL))],options={"verbose_name":"Push-Gerät","verbose_name_plural":"Push-Geräte"}),
    ]
