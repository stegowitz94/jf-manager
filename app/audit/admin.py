from django.contrib import admin
from .models import AuditEvent
@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display=("created_at","actor","action","object_type","object_repr")
    list_filter=("action","object_type","created_at")
    search_fields=("actor__username","object_repr","detail","path")
    readonly_fields=("actor","action","object_type","object_repr","detail","path","created_at")
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
