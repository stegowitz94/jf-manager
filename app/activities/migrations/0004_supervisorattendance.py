from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("activities", "0003_activitytypesetting"),
        ("supervisors", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SupervisorAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("present", "Anwesend"), ("excused", "Entschuldigt"), ("unexcused", "Unentschuldigt")], max_length=20, verbose_name="Status")),
                ("source", models.CharField(choices=[("manual", "Manuell"), ("leave", "Beurlaubung"), ("default", "Vorbelegung")], default="manual", max_length=20, verbose_name="Herkunft")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Geändert am")),
                ("activity", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="supervisor_attendances", to="activities.activity")),
                ("supervisor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attendances", to="supervisors.supervisor")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_supervisor_attendances", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Betreuer-Anwesenheit",
                "verbose_name_plural": "Betreuer-Anwesenheiten",
                "ordering": ("supervisor__last_name", "supervisor__first_name"),
            },
        ),
        migrations.AddConstraint(
            model_name="supervisorattendance",
            constraint=models.UniqueConstraint(fields=("activity", "supervisor"), name="unique_supervisor_attendance_per_activity"),
        ),
    ]
