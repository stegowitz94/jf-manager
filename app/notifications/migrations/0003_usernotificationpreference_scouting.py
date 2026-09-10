from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("notifications","0002_pushsubscription_usernotificationpreference")]
    operations=[migrations.AddField(model_name="usernotificationpreference",name="scouting",field=models.BooleanField(default=True,verbose_name="Schnupperdienst"))]
