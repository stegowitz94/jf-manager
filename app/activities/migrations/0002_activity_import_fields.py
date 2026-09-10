from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[("activities","0001_initial")]
    operations=[
        migrations.AddField(model_name="activity",name="import_source",field=models.CharField(choices=[("manual","Manuell"),("divera","DIVERA-Excel")],default="manual",max_length=20,verbose_name="Importquelle")),
        migrations.AddField(model_name="activity",name="imported_at",field=models.DateTimeField(blank=True,null=True,verbose_name="Importiert am")),
    ]
