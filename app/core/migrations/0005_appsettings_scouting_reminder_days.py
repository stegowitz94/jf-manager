from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("core","0004_scouting_dashboard_widgets")]
    operations=[migrations.AddField(model_name="appsettings",name="scouting_reminder_days",field=models.PositiveSmallIntegerField(default=14,verbose_name="Erinnerung vor Schnupperdienst in Tagen"))]
