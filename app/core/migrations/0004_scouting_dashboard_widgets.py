from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[("core","0003_appsettings_logo_dashboard_widgets")]
    operations=[
        migrations.AddField(model_name="appsettings",name="scouting_age_years",field=models.PositiveSmallIntegerField(default=16,verbose_name="Alter für Schnupperdienst")),
        migrations.AddField(model_name="appsettings",name="scouting_lead_months",field=models.PositiveSmallIntegerField(default=6,verbose_name="Vorlauf Schnupperdienst in Monaten")),
        migrations.AddField(model_name="dashboardpreference",name="show_today",field=models.BooleanField(default=True,verbose_name="Heute und offene Aufgaben")),
        migrations.AddField(model_name="dashboardpreference",name="show_scouting",field=models.BooleanField(default=True,verbose_name="Schnupperdienst")),
        migrations.AddField(model_name="dashboardpreference",name="show_recent_changes",field=models.BooleanField(default=True,verbose_name="Letzte Änderungen")),
    ]
