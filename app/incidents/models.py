from django.conf import settings
from django.db import models
from django.urls import reverse

from activities.models import Activity
from members.models import Guardian, Member
from supervisors.models import Supervisor


class Incident(models.Model):
    class RecordType(models.TextChoices):
        INCIDENT = "incident", "Vorfall"
        ACCIDENT = "accident", "Unfall"

    class Kind(models.TextChoices):
        GENERAL = "general", "Allgemeiner Vorfall"
        CONFLICT = "conflict", "Konflikt / Streit"
        DAMAGE = "damage", "Sachschaden"
        RULE = "rule", "Regel-/Ordnungsverstoß"
        OTHER = "other", "Sonstiges"

    record_type = models.CharField(
        "Dokumenttyp",
        max_length=20,
        choices=RecordType.choices,
        default=RecordType.INCIDENT,
    )
    occurred_at = models.DateTimeField("Datum / Uhrzeit")
    activity = models.ForeignKey(
        Activity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents",
        verbose_name="Zugehöriger Termin",
    )
    kind = models.CharField("Art des Vorfalls", max_length=20, choices=Kind.choices, default=Kind.GENERAL)
    title = models.CharField("Kurztitel", max_length=200)
    members = models.ManyToManyField(Member, blank=True, related_name="incidents", verbose_name="Betroffene Mitglieder")
    supervisors = models.ManyToManyField(
        Supervisor,
        blank=True,
        related_name="incidents",
        verbose_name="Betroffene Betreuer",
    )
    guardians = models.ManyToManyField(
        Guardian,
        blank=True,
        related_name="incidents",
        verbose_name="Betroffene Erziehungsberechtigte",
    )
    other_people = models.TextField("Sonstige betroffene / beteiligte Personen", blank=True)
    witnesses = models.TextField(
        "Zeugen",
        blank=True,
        help_text="Namen und ggf. Funktion der Zeugen. Keine unnötigen personenbezogenen Angaben erfassen.",
    )
    documentation = models.TextField("Dokumentation")

    # Unfallbezogene Angaben. Diese Felder werden ausschließlich im Unfallformular angezeigt.
    injured_members = models.ManyToManyField(Member, blank=True, related_name="injury_incidents", verbose_name="Verletzte Mitglieder")
    injured_supervisors = models.ManyToManyField(Supervisor, blank=True, related_name="injury_incidents", verbose_name="Verletzte Betreuer")
    injured_people = models.TextField("Sonstige verletzte Personen", blank=True)
    injury_description = models.TextField("Art der Verletzung / Beschwerden", blank=True)
    first_aid = models.TextField("Erste-Hilfe-Maßnahmen", blank=True)
    further_treatment = models.CharField("Weitere Behandlung", max_length=200, blank=True)
    guardians_informed = models.BooleanField("Erziehungsberechtigte informiert", default=False)
    guardians_informed_at = models.DateTimeField("Zeitpunkt der Information", null=True, blank=True)
    command_notification_sent_at = models.DateTimeField("Meldung an Wehrführung gesendet", null=True, blank=True)
    command_notification_sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_incident_notifications",
    )

    archived = models.BooleanField("Archiviert", default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_incidents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-occurred_at",)
        verbose_name = "Vorfall / Unfall"
        verbose_name_plural = "Vorfälle & Unfälle"

    def __str__(self):
        return f"{self.occurred_at:%d.%m.%Y} – {self.title}"

    def get_absolute_url(self):
        return reverse("incidents:detail", kwargs={"pk": self.pk})

    @property
    def is_accident(self):
        return self.record_type == self.RecordType.ACCIDENT
