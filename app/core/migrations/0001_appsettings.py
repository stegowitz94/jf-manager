from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="AppSettings", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("organisation_name", models.CharField(default="Jugendfeuerwehr", max_length=200, verbose_name="Name der Jugendfeuerwehr")),
        ("notification_recipients", models.TextField(blank=True, help_text="Mehrere E-Mail-Adressen durch Komma trennen. Benutzerkonten mit Jugendwart-/Admin-Rolle werden zusätzlich berücksichtigt.", verbose_name="Zusätzliche Benachrichtigungsempfänger")),
        ("unexcused_threshold", models.PositiveSmallIntegerField(default=3, verbose_name="Grenzwert unentschuldigt")),
        ("excused_threshold", models.PositiveSmallIntegerField(default=7, verbose_name="Grenzwert entschuldigt")),
        ("leave_notice_days", models.PositiveSmallIntegerField(default=14, verbose_name="Vorlauf Beurlaubungsende")),
        ("birthday_notifications", models.BooleanField(default=True, verbose_name="Geburtstagsmails")),
        ("absence_notifications", models.BooleanField(default=True, verbose_name="Fehlserienmails")),
        ("leave_notifications", models.BooleanField(default=True, verbose_name="Beurlaubungsmails")),
    ], options={"verbose_name":"JF-Manager-Einstellung","verbose_name_plural":"JF-Manager-Einstellungen"})]
