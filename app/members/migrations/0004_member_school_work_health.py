from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0003_member_street"),
    ]

    operations = [
        migrations.AddField(model_name="member", name="school_or_employer", field=models.CharField(blank=True, max_length=255, verbose_name="Schule oder Arbeitgeber")),
        migrations.AddField(model_name="member", name="vocational_training", field=models.CharField(blank=True, max_length=255, verbose_name="Berufsausbildung")),
        migrations.AddField(model_name="member", name="career_goal", field=models.CharField(blank=True, max_length=255, verbose_name="Voraussichtliches Berufsziel")),
        migrations.AddField(model_name="member", name="other_organizations", field=models.TextField(blank=True, verbose_name="Weitere Vereine oder Organisationen")),
        migrations.AddField(model_name="member", name="health_notes", field=models.TextField(blank=True, verbose_name="Krankheiten, Behinderungen, Beschwerden, Allergien oder sonstige gesundheitliche Hinweise")),
        migrations.AddField(model_name="member", name="swimming_status", field=models.CharField(blank=True, choices=[("swimmer", "Schwimmer"), ("non_swimmer", "Nichtschwimmer"), ("not_specified", "Keine Angabe")], default="not_specified", max_length=20, verbose_name="Schwimmfähigkeit")),
        migrations.AddField(model_name="member", name="health_insurance", field=models.CharField(blank=True, max_length=255, verbose_name="Krankenversicherung")),
    ]
