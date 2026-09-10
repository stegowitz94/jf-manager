from django.db import models


class AppSettings(models.Model):
    organisation_name = models.CharField("Name der Jugendfeuerwehr", max_length=200, default="Jugendfeuerwehr")
    short_name = models.CharField("Kurzbezeichnung", max_length=60, default="JF-Manager", blank=True)
    logo = models.ImageField("Logo", upload_to="organisation/", blank=True, null=True)
    fire_department_name = models.CharField("Feuerwehr / Träger", max_length=200, blank=True)
    federal_state = models.CharField("Bundesland", max_length=80, blank=True)
    street = models.CharField("Straße / Hausnummer", max_length=200, blank=True)
    postal_code = models.CharField("PLZ", max_length=20, blank=True)
    city = models.CharField("Ort", max_length=120, blank=True)
    contact_email = models.EmailField("Kontakt-E-Mail", blank=True)
    website = models.URLField("Webseite", blank=True)
    setup_complete = models.BooleanField("Ersteinrichtung abgeschlossen", default=False)
    setup_completed_at = models.DateTimeField("Ersteinrichtung abgeschlossen am", null=True, blank=True)
    notification_recipients = models.TextField(
        "Zusätzliche Benachrichtigungsempfänger", blank=True,
        help_text="Mehrere E-Mail-Adressen durch Komma trennen. Benutzerkonten mit Jugendwart-/Admin-Rolle werden zusätzlich berücksichtigt.",
    )
    unexcused_threshold = models.PositiveSmallIntegerField("Grenzwert unentschuldigt", default=3)
    excused_threshold = models.PositiveSmallIntegerField("Grenzwert entschuldigt", default=7)
    leave_notice_days = models.PositiveSmallIntegerField("Vorlauf Beurlaubungsende", default=14)
    birthday_notifications = models.BooleanField("Geburtstagsmails", default=True)
    absence_notifications = models.BooleanField("Fehlserienmails", default=True)
    leave_notifications = models.BooleanField("Beurlaubungsmails", default=True)
    scouting_age_years = models.PositiveSmallIntegerField("Alter für Schnupperdienst", default=16)
    scouting_lead_months = models.PositiveSmallIntegerField("Vorlauf Schnupperdienst in Monaten", default=6)
    scouting_reminder_days = models.PositiveSmallIntegerField("Erinnerung vor Schnupperdienst in Tagen", default=14)

    class Meta:
        verbose_name = "JF-Manager-Einstellung"
        verbose_name_plural = "JF-Manager-Einstellungen"

    def __str__(self):
        return self.organisation_name

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def recipient_list(self):
        return [x.strip() for x in self.notification_recipients.replace(";", ",").split(",") if x.strip()]


class ExternalLink(models.Model):
    name=models.CharField("Name",max_length=100)
    url=models.URLField("URL")
    icon=models.CharField("Icon",max_length=10,default="↗",blank=True)
    category=models.CharField("Kategorie",max_length=80,default="Werkzeuge",blank=True)
    visible=models.BooleanField("Sichtbar",default=True)
    favorite=models.BooleanField("Dashboard-Favorit",default=False)
    order=models.PositiveSmallIntegerField("Reihenfolge",default=10)
    class Meta:
        ordering=("order","name"); verbose_name="Externer Link"; verbose_name_plural="Externe Links"
    def __str__(self): return self.name

class DashboardPreference(models.Model):
    user=models.OneToOneField("accounts.User",on_delete=models.CASCADE,related_name="dashboard_preference")
    show_member_counts=models.BooleanField(default=True,verbose_name="Mitgliederzahlen")
    show_gender_chart=models.BooleanField(default=True,verbose_name="Geschlechterdiagramm")
    show_status_chart=models.BooleanField(default=True,verbose_name="Statusdiagramm")
    show_next_activities=models.BooleanField(default=True,verbose_name="Nächste Termine")
    show_birthdays=models.BooleanField(default=True,verbose_name="Geburtstage")
    show_waiting_list=models.BooleanField(default=True,verbose_name="Warteliste")
    show_attendance=models.BooleanField(default=True,verbose_name="Anwesenheit")
    show_quick_actions=models.BooleanField(default=True,verbose_name="Schnellaktionen")
    show_attendance_trend=models.BooleanField(default=True,verbose_name="Anwesenheitsentwicklung")
    show_favorite_links=models.BooleanField(default=True,verbose_name="Favoriten")
    show_today=models.BooleanField(default=True,verbose_name="Heute und offene Aufgaben")
    show_scouting=models.BooleanField(default=True,verbose_name="Schnupperdienst")
    show_recent_changes=models.BooleanField(default=True,verbose_name="Letzte Änderungen")
    widget_order=models.JSONField(default=list,blank=True,verbose_name="Widget-Reihenfolge")
    def __str__(self): return f"Dashboard von {self.user}"


class UserTablePreference(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="table_preferences")
    table_key = models.CharField(max_length=80)
    visible_columns = models.JSONField(default=list, blank=True)
    column_order = models.JSONField(default=list, blank=True)
    page_size = models.PositiveSmallIntegerField(default=25)
    filters = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("user", "table_key"), name="uniq_user_table_preference")]
        verbose_name = "Tabellen-Einstellung"
        verbose_name_plural = "Tabellen-Einstellungen"

    def __str__(self):
        return f"{self.user} · {self.table_key}"
