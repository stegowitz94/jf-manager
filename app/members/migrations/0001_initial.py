import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sequential_number", models.PositiveIntegerField(unique=True, verbose_name="Laufende Nummer")),
                ("first_name", models.CharField(max_length=100, verbose_name="Vorname")),
                ("last_name", models.CharField(max_length=100, verbose_name="Nachname")),
                ("gender", models.CharField(blank=True, choices=[("male", "Männlich"), ("female", "Weiblich"), ("diverse", "Divers"), ("not_specified", "Keine Angabe")], max_length=20, verbose_name="Geschlecht")),
                ("entry_date", models.DateField(blank=True, null=True, verbose_name="Beitrittsdatum")),
                ("jf_card_number", models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name="JF-Ausweisnummer")),
                ("activity_status", models.CharField(choices=[("active", "Aktiv"), ("on_leave", "Beurlaubt"), ("transition", "Übergang"), ("resigned", "Austritt")], default="active", max_length=20, verbose_name="Aktivität")),
                ("birth_date", models.DateField(verbose_name="Geburtsdatum")),
                ("postal_code", models.CharField(blank=True, max_length=10, verbose_name="PLZ")),
                ("city", models.CharField(blank=True, max_length=100, verbose_name="Ort")),
                ("phone", models.CharField(blank=True, max_length=50, verbose_name="Telefon")),
                ("mobile", models.CharField(blank=True, max_length=50, verbose_name="Mobil")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="E-Mail-Adresse")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Geändert am")),
            ],
            options={"verbose_name": "Mitglied", "verbose_name_plural": "Mitglieder", "ordering": ("last_name", "first_name")},
        ),
        migrations.CreateModel(
            name="Guardian",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("priority", models.PositiveSmallIntegerField(choices=[(1, "Erste erziehungsberechtigte Person"), (2, "Zweite erziehungsberechtigte Person")], verbose_name="Priorität")),
                ("first_name", models.CharField(max_length=100, verbose_name="Vorname")),
                ("last_name", models.CharField(max_length=100, verbose_name="Nachname")),
                ("phone", models.CharField(blank=True, max_length=50, verbose_name="Telefonnummer")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="E-Mail-Adresse")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="guardians", to="members.member", verbose_name="Mitglied")),
            ],
            options={"verbose_name": "Erziehungsberechtigte Person", "verbose_name_plural": "Erziehungsberechtigte Personen", "ordering": ("priority",)},
        ),
        migrations.CreateModel(
            name="MemberStatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("active", "Aktiv"), ("on_leave", "Beurlaubt"), ("transition", "Übergang"), ("resigned", "Austritt")], max_length=20, verbose_name="Status")),
                ("valid_from", models.DateField(default=django.utils.timezone.localdate, verbose_name="Gültig ab")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erfasst am")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="status_history", to="members.member", verbose_name="Mitglied")),
            ],
            options={"verbose_name": "Statusverlauf", "verbose_name_plural": "Statusverläufe", "ordering": ("-valid_from", "-created_at")},
        ),
        migrations.CreateModel(
            name="Leave",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateField(verbose_name="Beginn")),
                ("planned_end_date", models.DateField(verbose_name="Geplantes Ende")),
                ("note", models.TextField(blank=True, verbose_name="Bemerkung")),
                ("status_after", models.CharField(choices=[("active", "Aktiv"), ("on_leave", "Beurlaubt"), ("transition", "Übergang"), ("resigned", "Austritt")], default="active", max_length=20, verbose_name="Status danach")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Geändert am")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_leaves", to=settings.AUTH_USER_MODEL)),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="leaves", to="members.member", verbose_name="Mitglied")),
            ],
            options={"verbose_name": "Beurlaubung", "verbose_name_plural": "Beurlaubungen", "ordering": ("-start_date",)},
        ),
        migrations.AddConstraint(
            model_name="guardian",
            constraint=models.UniqueConstraint(fields=("member", "priority"), name="unique_guardian_priority_per_member"),
        ),
        migrations.AddConstraint(
            model_name="leave",
            constraint=models.CheckConstraint(condition=models.Q(("planned_end_date__gte", models.F("start_date"))), name="leave_end_not_before_start"),
        ),
    ]
