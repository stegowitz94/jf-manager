# Generated for JF-Manager 0.3
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("members", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="Thema")),
                ("activity_type", models.CharField(choices=[("group", "Gruppenstunde"), ("drill", "Übungsdienst"), ("event", "Veranstaltung"), ("camp", "Zeltlager"), ("other", "Sonstiger Termin")], default="group", max_length=20, verbose_name="Terminart")),
                ("starts_at", models.DateTimeField(verbose_name="Beginn")),
                ("ends_at", models.DateTimeField(blank=True, null=True, verbose_name="Ende")),
                ("location", models.CharField(blank=True, max_length=200, verbose_name="Ort")),
                ("description", models.TextField(blank=True, verbose_name="Beschreibung")),
                ("attendance_completed", models.BooleanField(default=False, verbose_name="Anwesenheit abgeschlossen")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Geändert am")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_activities", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Termin", "verbose_name_plural": "Termine", "ordering": ("-starts_at",)},
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("present", "Anwesend"), ("excused", "Entschuldigt"), ("unexcused", "Unentschuldigt")], max_length=20, verbose_name="Status")),
                ("source", models.CharField(choices=[("manual", "Manuell"), ("leave", "Beurlaubung"), ("default", "Vorbelegung")], default="manual", max_length=20, verbose_name="Herkunft")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Geändert am")),
                ("activity", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendances", to="activities.activity")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attendances", to="members.member")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_attendances", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Anwesenheit", "verbose_name_plural": "Anwesenheiten", "ordering": ("member__last_name", "member__first_name")},
        ),
        migrations.AddConstraint(
            model_name="attendance",
            constraint=models.UniqueConstraint(fields=("activity", "member"), name="unique_attendance_per_activity_member"),
        ),
    ]
