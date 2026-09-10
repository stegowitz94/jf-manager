from django.db import migrations, models


def classify_existing_records(apps, schema_editor):
    Incident = apps.get_model("incidents", "Incident")
    Incident.objects.filter(kind="accident").update(record_type="accident", kind="general")


class Migration(migrations.Migration):
    dependencies = [("incidents", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="incident",
            name="record_type",
            field=models.CharField(
                choices=[("incident", "Vorfall"), ("accident", "Unfall")],
                default="incident",
                max_length=20,
                verbose_name="Dokumenttyp",
            ),
        ),
        migrations.RunPython(classify_existing_records, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="incident",
            name="kind",
            field=models.CharField(
                choices=[
                    ("general", "Allgemeiner Vorfall"),
                    ("conflict", "Konflikt / Streit"),
                    ("damage", "Sachschaden"),
                    ("rule", "Regel-/Ordnungsverstoß"),
                    ("other", "Sonstiges"),
                ],
                default="general",
                max_length=20,
                verbose_name="Art des Vorfalls",
            ),
        ),
        migrations.AlterModelOptions(
            name="incident",
            options={"ordering": ("-occurred_at",), "verbose_name": "Vorfall / Unfall", "verbose_name_plural": "Vorfälle & Unfälle"},
        ),
    ]
