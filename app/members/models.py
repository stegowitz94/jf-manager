from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Member(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Männlich"
        FEMALE = "female", "Weiblich"
        DIVERSE = "diverse", "Divers"
        NOT_SPECIFIED = "not_specified", "Keine Angabe"

    class ActivityStatus(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        ON_LEAVE = "on_leave", "Beurlaubt"
        TRANSITION = "transition", "Übergang"
        RESIGNED = "resigned", "Austritt"

    sequential_number = models.PositiveIntegerField("Laufende Nummer", unique=True)
    first_name = models.CharField("Vorname", max_length=100)
    last_name = models.CharField("Nachname", max_length=100)
    gender = models.CharField("Geschlecht", max_length=20, choices=Gender.choices, blank=True)
    entry_date = models.DateField("Beitrittsdatum", null=True, blank=True)
    jf_card_number = models.CharField("JF-Ausweisnummer", max_length=50, unique=True, null=True, blank=True)
    activity_status = models.CharField(
        "Aktivität", max_length=20, choices=ActivityStatus.choices, default=ActivityStatus.ACTIVE
    )
    birth_date = models.DateField("Geburtsdatum")
    street = models.CharField("Straße und Hausnummer", max_length=200, blank=True)
    postal_code = models.CharField("PLZ", max_length=10, blank=True)
    city = models.CharField("Ort", max_length=100, blank=True)
    phone = models.CharField("Telefon", max_length=50, blank=True)
    mobile = models.CharField("Mobil", max_length=50, blank=True)
    email = models.EmailField("E-Mail-Adresse", blank=True)
    profile_image = models.ImageField("Profilbild", upload_to="members/profile_images/", blank=True, null=True)
    photo_video_permission = models.BooleanField("Foto-/Videoeinwilligung erteilt", default=False)
    divera_permission = models.BooleanField("DIVERA-Einwilligung erteilt", default=False)

    class SwimmingStatus(models.TextChoices):
        SWIMMER = "swimmer", "Schwimmer"
        NON_SWIMMER = "non_swimmer", "Nichtschwimmer"
        NOT_SPECIFIED = "not_specified", "Keine Angabe"

    school_or_employer = models.CharField("Schule oder Arbeitgeber", max_length=255, blank=True)
    vocational_training = models.CharField("Berufsausbildung", max_length=255, blank=True)
    career_goal = models.CharField("Voraussichtliches Berufsziel", max_length=255, blank=True)
    other_organizations = models.TextField("Weitere Vereine oder Organisationen", blank=True)
    health_notes = models.TextField(
        "Krankheiten, Behinderungen, Beschwerden, Allergien oder sonstige gesundheitliche Hinweise",
        blank=True,
    )
    swimming_status = models.CharField(
        "Schwimmfähigkeit",
        max_length=20,
        choices=SwimmingStatus.choices,
        default=SwimmingStatus.NOT_SPECIFIED,
        blank=True,
    )
    health_insurance = models.CharField("Krankenversicherung", max_length=255, blank=True)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)
    updated_at = models.DateTimeField("Geändert am", auto_now=True)

    class Meta:
        ordering = ("last_name", "first_name")
        verbose_name = "Mitglied"
        verbose_name_plural = "Mitglieder"

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def get_absolute_url(self):
        return reverse("members:detail", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs):
        image = self.profile_image
        super().delete(*args, **kwargs)
        if image:
            image.storage.delete(image.name)


class Guardian(models.Model):
    class Priority(models.IntegerChoices):
        PRIMARY = 1, "Erste erziehungsberechtigte Person"
        SECONDARY = 2, "Zweite erziehungsberechtigte Person"

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="guardians", verbose_name="Mitglied")
    priority = models.PositiveSmallIntegerField("Priorität", choices=Priority.choices)
    first_name = models.CharField("Vorname", max_length=100)
    last_name = models.CharField("Nachname", max_length=100)
    phone = models.CharField("Telefonnummer", max_length=50, blank=True)
    email = models.EmailField("E-Mail-Adresse", blank=True)
    class Meta:
        ordering = ("priority",)
        verbose_name = "Erziehungsberechtigte Person"
        verbose_name_plural = "Erziehungsberechtigte Personen"
        constraints = [
            models.UniqueConstraint(fields=("member", "priority"), name="unique_guardian_priority_per_member")
        ]

    def clean(self):
        super().clean()
        if not self.phone and not self.email:
            raise ValidationError("Bitte mindestens eine Telefonnummer oder E-Mail-Adresse angeben.")
        if self.member_id:
            count = Guardian.objects.filter(member_id=self.member_id).exclude(pk=self.pk).count()
            if count >= 2:
                raise ValidationError("Pro Mitglied können höchstens zwei erziehungsberechtigte Personen hinterlegt werden.")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class MemberStatusHistory(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="status_history", verbose_name="Mitglied")
    status = models.CharField("Status", max_length=20, choices=Member.ActivityStatus.choices)
    valid_from = models.DateField("Gültig ab", default=timezone.localdate)
    created_at = models.DateTimeField("Erfasst am", auto_now_add=True)

    class Meta:
        ordering = ("-valid_from", "-created_at")
        verbose_name = "Statusverlauf"
        verbose_name_plural = "Statusverläufe"

    def __str__(self):
        return f"{self.member}: {self.get_status_display()} ab {self.valid_from:%d.%m.%Y}"


class Leave(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="leaves", verbose_name="Mitglied")
    start_date = models.DateField("Beginn")
    planned_end_date = models.DateField("Geplantes Ende")
    note = models.TextField("Bemerkung", blank=True)
    status_after = models.CharField(
        "Status danach", max_length=20, choices=Member.ActivityStatus.choices, default=Member.ActivityStatus.ACTIVE
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_leaves"
    )
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)
    updated_at = models.DateTimeField("Geändert am", auto_now=True)

    class Meta:
        ordering = ("-start_date",)
        verbose_name = "Beurlaubung"
        verbose_name_plural = "Beurlaubungen"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(planned_end_date__gte=models.F("start_date")), name="leave_end_not_before_start"
            )
        ]

    def clean(self):
        super().clean()
        if self.start_date and self.planned_end_date and self.planned_end_date < self.start_date:
            raise ValidationError({"planned_end_date": "Das geplante Ende darf nicht vor dem Beginn liegen."})

    @property
    def is_current(self):
        today = timezone.localdate()
        return self.start_date <= today <= self.planned_end_date

    def __str__(self):
        return f"{self.member}: {self.start_date:%d.%m.%Y} bis {self.planned_end_date:%d.%m.%Y}"


class MemberBadge(models.Model):
    class BadgeType(models.TextChoices):
        YOUTH_FLAME_1 = "youth_flame_1", "Jugendflamme Stufe 1"
        YOUTH_FLAME_2 = "youth_flame_2", "Jugendflamme Stufe 2"
        YOUTH_FLAME_3 = "youth_flame_3", "Jugendflamme Stufe 3"
        PERFORMANCE_BADGE = "performance_badge", "Leistungsspange"
        OTHER = "other", "Sonstiges Abzeichen / Auszeichnung"
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="badges", verbose_name="Mitglied")
    badge_type = models.CharField("Abzeichen", max_length=40, choices=BadgeType.choices)
    custom_name = models.CharField("Bezeichnung", max_length=200, blank=True)
    awarded_on = models.DateField("Datum")
    note = models.TextField("Bemerkung", blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_member_badges")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("-awarded_on", "badge_type")
        verbose_name = "Abzeichen / Auszeichnung"
        verbose_name_plural = "Abzeichen & Auszeichnungen"
    def __str__(self):
        return self.custom_name if self.badge_type == self.BadgeType.OTHER and self.custom_name else self.get_badge_type_display()
