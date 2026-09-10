from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[migrations.CreateModel(name="AuditEvent",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("action",models.CharField(max_length=80,verbose_name="Aktion")),("object_type",models.CharField(blank=True,max_length=100,verbose_name="Objekttyp")),("object_repr",models.CharField(blank=True,max_length=255,verbose_name="Objekt")),("detail",models.TextField(blank=True,verbose_name="Details")),("path",models.CharField(blank=True,max_length=300,verbose_name="Pfad")),("created_at",models.DateTimeField(auto_now_add=True,verbose_name="Zeitpunkt")),("actor",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL,verbose_name="Benutzer"))],options={"verbose_name":"Audit-Ereignis","verbose_name_plural":"Audit-Protokoll","ordering":("-created_at",)})]
