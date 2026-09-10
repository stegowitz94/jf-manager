from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[("activities","0004_supervisorattendance")]
    operations=[migrations.AddField(model_name="activity",name="participation_mode",field=models.CharField(choices=[("mandatory","Verpflichtend"),("voluntary","Freiwillig")],default="mandatory",help_text="Freiwillige Gruppenstunden werden nicht in Anwesenheitsstatistiken und Fehlserien berücksichtigt.",max_length=20,verbose_name="Teilnahme"))]
