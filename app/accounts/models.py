from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        YOUTH_WARDEN = "youth_warden", "Jugendfeuerwehrwart"
        DEPUTY_YOUTH_WARDEN = "deputy_youth_warden", "Stellvertretender Jugendfeuerwehrwart"
        SUPERVISOR = "supervisor", "Betreuer"
        READ_ONLY = "read_only", "Leseberechtigung"
    role = models.CharField("Rolle", max_length=32, choices=Role.choices, default=Role.YOUTH_WARDEN)
    supervisor = models.OneToOneField(
        "supervisors.Supervisor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_account",
        verbose_name="Zugeordneter Betreuer",
    )
    def __str__(self):
        return self.get_full_name() or self.username
