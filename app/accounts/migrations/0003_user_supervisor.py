from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_user_groups"),
        ("supervisors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="supervisor",
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="user_account", to="supervisors.supervisor", verbose_name="Zugeordneter Betreuer"),
        ),
    ]
