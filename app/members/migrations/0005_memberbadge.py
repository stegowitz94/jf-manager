from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[("members","0004_member_school_work_health"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[migrations.CreateModel(
        name="MemberBadge",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("badge_type", models.CharField(choices=[("youth_flame_1","Jugendflamme Stufe 1"),("youth_flame_2","Jugendflamme Stufe 2"),("youth_flame_3","Jugendflamme Stufe 3"),("performance_badge","Leistungsspange"),("other","Sonstiges Abzeichen / Auszeichnung")], max_length=40, verbose_name="Abzeichen")),
            ("custom_name", models.CharField(blank=True,max_length=200,verbose_name="Bezeichnung")),
            ("awarded_on", models.DateField(verbose_name="Datum")),
            ("note", models.TextField(blank=True,verbose_name="Bemerkung")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("updated_at", models.DateTimeField(auto_now=True)),
            ("created_by", models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="created_member_badges",to=settings.AUTH_USER_MODEL)),
            ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="badges",to="members.member",verbose_name="Mitglied")),
        ], options={"verbose_name":"Abzeichen / Auszeichnung","verbose_name_plural":"Abzeichen & Auszeichnungen","ordering":("-awarded_on","badge_type")}
    )]
