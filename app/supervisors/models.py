from pathlib import Path

from django.db import models
from django.urls import reverse


class SupervisorFunction(models.Model):
    name = models.CharField("Bezeichnung", max_length=100, unique=True)
    sort_order = models.PositiveSmallIntegerField("Sortierung", default=100)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = "Betreuerfunktion"
        verbose_name_plural = "Betreuerfunktionen"

    def __str__(self):
        return self.name


class Supervisor(models.Model):
    class ActivityStatus(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        ON_LEAVE = "on_leave", "Beurlaubt"
        LEFT = "left", "Ausgeschieden"

    sequential_number = models.PositiveIntegerField("Laufende Nummer", unique=True)
    first_name = models.CharField("Vorname", max_length=100)
    last_name = models.CharField("Nachname", max_length=100)
    birth_date = models.DateField("Geburtsdatum", null=True, blank=True)
    entry_date = models.DateField("Eintrittsdatum", null=True, blank=True)
    activity_status = models.CharField(
        "Aktivität", max_length=20, choices=ActivityStatus.choices, default=ActivityStatus.ACTIVE
    )
    phone = models.CharField("Telefon", max_length=50, blank=True)
    mobile = models.CharField("Mobil", max_length=50, blank=True)
    email = models.EmailField("E-Mail-Adresse", blank=True)
    functions = models.ManyToManyField(SupervisorFunction, blank=True, related_name="supervisors", verbose_name="Funktionen")
    profile_image = models.ImageField("Profilbild", upload_to="supervisors/profile_images/", blank=True, null=True)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)
    updated_at = models.DateTimeField("Geändert am", auto_now=True)

    class Meta:
        ordering = ("last_name", "first_name")
        verbose_name = "Betreuer"
        verbose_name_plural = "Betreuer"

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def get_absolute_url(self):
        return reverse("supervisors:detail", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs):
        image = self.profile_image
        super().delete(*args, **kwargs)
        if image:
            image.storage.delete(image.name)


class SupervisorTraining(models.Model):
    supervisor=models.ForeignKey(Supervisor,on_delete=models.CASCADE,related_name="trainings",verbose_name="Betreuer")
    title=models.CharField("Fortbildung / Qualifikation",max_length=200)
    category=models.CharField("Kategorie",max_length=100,blank=True)
    provider=models.CharField("Veranstalter",max_length=200,blank=True)
    completed_on=models.DateField("Datum")
    valid_until=models.DateField("Gültig bis / Wiedervorlage",null=True,blank=True)
    duration_units=models.PositiveSmallIntegerField("Dauer / UE",null=True,blank=True)
    note=models.TextField("Bemerkung",blank=True)
    certificate=models.FileField("Nachweis",upload_to="supervisors/training_certificates/",blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=("-completed_on",); verbose_name="Betreuer-Fortbildung"; verbose_name_plural="Betreuer-Fortbildungen"
    def __str__(self): return f"{self.supervisor}: {self.title}"
