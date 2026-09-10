from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("members", "0002_member_permissions_and_profile_image")]

    operations = [
        migrations.AddField(
            model_name="member",
            name="street",
            field=models.CharField(blank=True, max_length=200, verbose_name="Straße und Hausnummer"),
        ),
    ]
