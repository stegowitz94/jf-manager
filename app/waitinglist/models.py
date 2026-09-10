from django.db import models
from django.urls import reverse

class WaitingListEntry(models.Model):
    class Status(models.TextChoices):
        WAITING="waiting","Wartend"
        CONTACTED="contacted","Kontaktiert"
        TRIAL="trial","Probeteilnahme"
        PLANNED="planned","Aufnahme vorgesehen"
        ADMITTED="admitted","Aufgenommen"
        DECLINED="declined","Abgesagt"
    first_name=models.CharField("Vorname",max_length=100)
    last_name=models.CharField("Nachname",max_length=100)
    birth_date=models.DateField("Geburtsdatum",null=True,blank=True)
    phone=models.CharField("Telefon",max_length=50,blank=True)
    email=models.EmailField("E-Mail-Adresse",blank=True)
    street=models.CharField("Straße und Hausnummer",max_length=200,blank=True)
    postal_code=models.CharField("PLZ",max_length=10,blank=True)
    city=models.CharField("Wohnort",max_length=100,blank=True)
    desired_entry_date=models.DateField("Gewünschter Eintritt",null=True,blank=True)
    note=models.TextField("Bemerkung",blank=True)
    status=models.CharField("Status",max_length=20,choices=Status.choices,default=Status.WAITING)
    created_at=models.DateTimeField("Eingetragen am",auto_now_add=True)
    updated_at=models.DateTimeField("Geändert am",auto_now=True)
    class Meta:
        ordering=("created_at","last_name","first_name")
        verbose_name="Wartelisteneintrag"
        verbose_name_plural="Wartelisteneinträge"
    def __str__(self): return f"{self.last_name}, {self.first_name}"
    def get_absolute_url(self): return reverse("waitinglist:detail",kwargs={"pk":self.pk})
