from django.conf import settings
from django.db import models
class AuditEvent(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Benutzer")
    action=models.CharField("Aktion",max_length=80)
    object_type=models.CharField("Objekttyp",max_length=100,blank=True)
    object_repr=models.CharField("Objekt",max_length=255,blank=True)
    detail=models.TextField("Details",blank=True)
    path=models.CharField("Pfad",max_length=300,blank=True)
    created_at=models.DateTimeField("Zeitpunkt",auto_now_add=True)
    class Meta:
        ordering=("-created_at",); verbose_name="Audit-Ereignis"; verbose_name_plural="Audit-Protokoll"
