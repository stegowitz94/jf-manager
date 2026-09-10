from django.db import migrations, models
import django.utils.timezone


def mark_existing_configured(apps, schema_editor):
    AppSettings = apps.get_model('core', 'AppSettings')
    # Any settings row that already exists belongs to an upgraded installation.
    AppSettings.objects.all().update(setup_complete=True, setup_completed_at=django.utils.timezone.now())


class Migration(migrations.Migration):
    dependencies = [('core', '0006_usertablepreference')]
    operations = [
        migrations.AddField(model_name='appsettings', name='fire_department_name', field=models.CharField(blank=True, max_length=200, verbose_name='Feuerwehr / Träger')),
        migrations.AddField(model_name='appsettings', name='federal_state', field=models.CharField(blank=True, max_length=80, verbose_name='Bundesland')),
        migrations.AddField(model_name='appsettings', name='street', field=models.CharField(blank=True, max_length=200, verbose_name='Straße / Hausnummer')),
        migrations.AddField(model_name='appsettings', name='postal_code', field=models.CharField(blank=True, max_length=20, verbose_name='PLZ')),
        migrations.AddField(model_name='appsettings', name='city', field=models.CharField(blank=True, max_length=120, verbose_name='Ort')),
        migrations.AddField(model_name='appsettings', name='contact_email', field=models.EmailField(blank=True, max_length=254, verbose_name='Kontakt-E-Mail')),
        migrations.AddField(model_name='appsettings', name='website', field=models.URLField(blank=True, verbose_name='Webseite')),
        migrations.AddField(model_name='appsettings', name='setup_complete', field=models.BooleanField(default=False, verbose_name='Ersteinrichtung abgeschlossen')),
        migrations.AddField(model_name='appsettings', name='setup_completed_at', field=models.DateTimeField(blank=True, null=True, verbose_name='Ersteinrichtung abgeschlossen am')),
        migrations.RunPython(mark_existing_configured, migrations.RunPython.noop),
    ]
