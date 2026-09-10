from django.conf import settings
from django.db import models
from django.urls import reverse
from members.models import Member
from supervisors.models import Supervisor

class Activity(models.Model):
    class ActivityType(models.TextChoices):
        GROUP="group","Gruppenstunde"; DRILL="drill","Übungsdienst"; EVENT="event","Veranstaltung"; CAMP="camp","Zeltlager"; OTHER="other","Sonstiger Termin"
    class ParticipationMode(models.TextChoices):
        MANDATORY="mandatory","Verpflichtend"
        VOLUNTARY="voluntary","Freiwillig"
    class ImportSource(models.TextChoices):
        MANUAL="manual","Manuell"; DIVERA="divera","DIVERA-Excel"
    title=models.CharField("Thema",max_length=200)
    activity_type=models.CharField("Terminart",max_length=20,choices=ActivityType.choices,default=ActivityType.GROUP)
    starts_at=models.DateTimeField("Beginn")
    participation_mode=models.CharField("Teilnahme",max_length=20,choices=ParticipationMode.choices,default=ParticipationMode.MANDATORY,help_text="Freiwillige Gruppenstunden werden nicht in Anwesenheitsstatistiken und Fehlserien berücksichtigt.")
    ends_at=models.DateTimeField("Ende",null=True,blank=True)
    location=models.CharField("Ort",max_length=200,blank=True)
    description=models.TextField("Beschreibung",blank=True)
    attendance_completed=models.BooleanField("Anwesenheit abgeschlossen",default=False)
    import_source=models.CharField("Importquelle",max_length=20,choices=ImportSource.choices,default=ImportSource.MANUAL)
    imported_at=models.DateTimeField("Importiert am",null=True,blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_activities")
    created_at=models.DateTimeField("Erstellt am",auto_now_add=True)
    updated_at=models.DateTimeField("Geändert am",auto_now=True)
    class Meta:
        ordering=("-starts_at",); verbose_name="Termin"; verbose_name_plural="Termine"
    def __str__(self): return f"{self.starts_at:%d.%m.%Y} – {self.title}"
    def get_absolute_url(self): return reverse("activities:attendance",kwargs={"pk":self.pk})
    @property
    def counts_for_attendance_statistics(self):
        return not (self.activity_type == self.ActivityType.GROUP and self.participation_mode == self.ParticipationMode.VOLUNTARY)

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT="present","Anwesend"; EXCUSED="excused","Entschuldigt"; UNEXCUSED="unexcused","Unentschuldigt"
    class Source(models.TextChoices):
        MANUAL="manual","Manuell"; LEAVE="leave","Beurlaubung"; DEFAULT="default","Vorbelegung"
    activity=models.ForeignKey(Activity,on_delete=models.CASCADE,related_name="attendances")
    member=models.ForeignKey(Member,on_delete=models.PROTECT,related_name="attendances")
    status=models.CharField("Status",max_length=20,choices=Status.choices)
    source=models.CharField("Herkunft",max_length=20,choices=Source.choices,default=Source.MANUAL)
    updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="updated_attendances")
    updated_at=models.DateTimeField("Geändert am",auto_now=True)
    class Meta:
        ordering=("member__last_name","member__first_name"); verbose_name="Anwesenheit"; verbose_name_plural="Anwesenheiten"
        constraints=[models.UniqueConstraint(fields=("activity","member"),name="unique_attendance_per_activity_member")]
    def __str__(self): return f"{self.activity}: {self.member} – {self.get_status_display()}"


class SupervisorAttendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Anwesend"
        EXCUSED = "excused", "Entschuldigt"
        UNEXCUSED = "unexcused", "Unentschuldigt"

    class Source(models.TextChoices):
        MANUAL = "manual", "Manuell"
        LEAVE = "leave", "Beurlaubung"
        DEFAULT = "default", "Vorbelegung"

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="supervisor_attendances")
    supervisor = models.ForeignKey(Supervisor, on_delete=models.PROTECT, related_name="attendances")
    status = models.CharField("Status", max_length=20, choices=Status.choices)
    source = models.CharField("Herkunft", max_length=20, choices=Source.choices, default=Source.MANUAL)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_supervisor_attendances",
    )
    updated_at = models.DateTimeField("Geändert am", auto_now=True)

    class Meta:
        ordering = ("supervisor__last_name", "supervisor__first_name")
        verbose_name = "Betreuer-Anwesenheit"
        verbose_name_plural = "Betreuer-Anwesenheiten"
        constraints = [
            models.UniqueConstraint(
                fields=("activity", "supervisor"),
                name="unique_supervisor_attendance_per_activity",
            )
        ]

    def __str__(self):
        return f"{self.activity}: {self.supervisor} – {self.get_status_display()}"


class ActivityTypeSetting(models.Model):
    activity_type = models.CharField(
        "Terminart",
        max_length=20,
        choices=Activity.ActivityType.choices,
        unique=True,
    )
    default_start_time = models.TimeField("Standardbeginn", null=True, blank=True)
    default_end_time = models.TimeField("Standardende", null=True, blank=True)

    class Meta:
        ordering = ("activity_type",)
        verbose_name = "Standardzeit einer Terminart"
        verbose_name_plural = "Standardzeiten der Terminarten"

    def __str__(self):
        return self.get_activity_type_display()
