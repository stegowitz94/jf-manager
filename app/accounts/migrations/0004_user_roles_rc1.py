from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_user_supervisor")]
    operations = [
        migrations.AlterField(
            model_name="user", name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Administrator"),
                    ("youth_warden", "Jugendfeuerwehrwart"),
                    ("deputy_youth_warden", "Stellvertretender Jugendfeuerwehrwart"),
                    ("supervisor", "Betreuer"),
                    ("read_only", "Leseberechtigung"),
                ], default="youth_warden", max_length=32, verbose_name="Rolle"
            ),
        ),
    ]
