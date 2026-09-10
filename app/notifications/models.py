from django.db import models
class NotificationLog(models.Model):
    event_key=models.CharField("Ereignisschlüssel",max_length=255,unique=True)
    notification_type=models.CharField("Typ",max_length=50)
    subject=models.CharField("Betreff",max_length=255)
    recipients=models.TextField("Empfänger")
    status=models.CharField("Status",max_length=20,choices=(("sent","Versendet"),("failed","Fehlgeschlagen")))
    error=models.TextField("Fehler",blank=True)
    created_at=models.DateTimeField("Zeitpunkt",auto_now_add=True)
    class Meta:
        ordering=("-created_at",); verbose_name="Benachrichtigung"; verbose_name_plural="Benachrichtigungen"
    def __str__(self): return self.subject


class UserNotificationPreference(models.Model):
    user=models.OneToOneField("accounts.User",on_delete=models.CASCADE,related_name="notification_preference")
    email_enabled=models.BooleanField("E-Mail",default=True)
    push_enabled=models.BooleanField("Push",default=False)
    birthdays=models.BooleanField("Geburtstage",default=True)
    absences=models.BooleanField("Fehlserien",default=True)
    leave_end=models.BooleanField("Beurlaubungsende",default=True)
    upcoming_activity=models.BooleanField("Nächster Termin",default=True)
    scouting=models.BooleanField("Schnupperdienst",default=True)
    def __str__(self): return f"Benachrichtigungen von {self.user}"

class PushSubscription(models.Model):
    user=models.ForeignKey("accounts.User",on_delete=models.CASCADE,related_name="push_subscriptions")
    endpoint=models.URLField(max_length=1000,unique=True)
    p256dh=models.TextField()
    auth=models.TextField()
    user_agent=models.CharField(max_length=500,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    last_seen_at=models.DateTimeField(auto_now=True)
    class Meta: verbose_name="Push-Gerät"; verbose_name_plural="Push-Geräte"
    def __str__(self): return f"{self.user} · {self.endpoint[:50]}"
