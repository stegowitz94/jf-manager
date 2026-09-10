from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[("core","0005_appsettings_scouting_reminder_days"),("accounts","0003_user_supervisor")]
    operations=[
        migrations.CreateModel(
            name="UserTablePreference",
            fields=[
                ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
                ("table_key",models.CharField(max_length=80)),
                ("visible_columns",models.JSONField(blank=True,default=list)),
                ("column_order",models.JSONField(blank=True,default=list)),
                ("page_size",models.PositiveSmallIntegerField(default=25)),
                ("filters",models.JSONField(blank=True,default=dict)),
                ("user",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="table_preferences",to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name":"Tabellen-Einstellung","verbose_name_plural":"Tabellen-Einstellungen"},
        ),
        migrations.AddConstraint(model_name="usertablepreference",constraint=models.UniqueConstraint(fields=("user","table_key"),name="uniq_user_table_preference")),
    ]
