from django.db import migrations, models


def create_default_functions(apps, schema_editor):
    Function = apps.get_model("supervisors", "SupervisorFunction")
    names = [
        "Jugendfeuerwehrwart",
        "Stellvertretender Jugendfeuerwehrwart",
        "Betreuer",
        "Hilfsbetreuer",
        "Maschinist",
    ]
    for index, name in enumerate(names, start=1):
        Function.objects.get_or_create(name=name, defaults={"sort_order": index * 10})


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="SupervisorFunction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Bezeichnung")),
                ("sort_order", models.PositiveSmallIntegerField(default=100, verbose_name="Sortierung")),
                ("active", models.BooleanField(default=True, verbose_name="Aktiv")),
            ],
            options={"verbose_name": "Betreuerfunktion", "verbose_name_plural": "Betreuerfunktionen", "ordering": ("sort_order", "name")},
        ),
        migrations.CreateModel(
            name="Supervisor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sequential_number", models.PositiveIntegerField(unique=True, verbose_name="Laufende Nummer")),
                ("first_name", models.CharField(max_length=100, verbose_name="Vorname")),
                ("last_name", models.CharField(max_length=100, verbose_name="Nachname")),
                ("birth_date", models.DateField(blank=True, null=True, verbose_name="Geburtsdatum")),
                ("entry_date", models.DateField(blank=True, null=True, verbose_name="Eintrittsdatum")),
                ("activity_status", models.CharField(choices=[("active", "Aktiv"), ("on_leave", "Beurlaubt"), ("left", "Ausgeschieden")], default="active", max_length=20, verbose_name="Aktivität")),
                ("phone", models.CharField(blank=True, max_length=50, verbose_name="Telefon")),
                ("mobile", models.CharField(blank=True, max_length=50, verbose_name="Mobil")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="E-Mail-Adresse")),
                ("profile_image", models.ImageField(blank=True, null=True, upload_to="supervisors/profile_images/", verbose_name="Profilbild")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Geändert am")),
                ("functions", models.ManyToManyField(blank=True, related_name="supervisors", to="supervisors.supervisorfunction", verbose_name="Funktionen")),
            ],
            options={"verbose_name": "Betreuer", "verbose_name_plural": "Betreuer", "ordering": ("last_name", "first_name")},
        ),
        migrations.RunPython(create_default_functions, migrations.RunPython.noop),
    ]
