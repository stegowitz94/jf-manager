from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("members", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="member",
            name="divera_permission",
            field=models.BooleanField(default=False, verbose_name="DIVERA-Einwilligung erteilt"),
        ),
        migrations.AddField(
            model_name="member",
            name="photo_video_permission",
            field=models.BooleanField(default=False, verbose_name="Foto-/Videoeinwilligung erteilt"),
        ),
        migrations.AddField(
            model_name="member",
            name="profile_image",
            field=models.ImageField(blank=True, null=True, upload_to="members/profile_images/", verbose_name="Profilbild"),
        ),
    ]
