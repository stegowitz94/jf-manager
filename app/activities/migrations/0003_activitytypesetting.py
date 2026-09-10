from datetime import time
from django.db import migrations, models


def seed_default_times(apps, schema_editor):
    Setting = apps.get_model("activities", "ActivityTypeSetting")
    for activity_type in ("group", "drill"):
        Setting.objects.get_or_create(
            activity_type=activity_type,
            defaults={"default_start_time": time(17, 15), "default_end_time": time(18, 45)},
        )


class Migration(migrations.Migration):
    dependencies = [("activities", "0002_activity_import_fields")]
    operations = [
        migrations.CreateModel(
            name="ActivityTypeSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("activity_type", models.CharField(choices=[("group", "Gruppenstunde"), ("drill", "Übungsdienst"), ("event", "Veranstaltung"), ("camp", "Zeltlager"), ("other", "Sonstiger Termin")], max_length=20, unique=True, verbose_name="Terminart")),
                ("default_start_time", models.TimeField(blank=True, null=True, verbose_name="Standardbeginn")),
                ("default_end_time", models.TimeField(blank=True, null=True, verbose_name="Standardende")),
            ],
            options={"verbose_name": "Standardzeit einer Terminart", "verbose_name_plural": "Standardzeiten der Terminarten", "ordering": ("activity_type",)},
        ),
        migrations.RunPython(seed_default_times, migrations.RunPython.noop),
    ]
