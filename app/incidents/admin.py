from django.contrib import admin

from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "record_type", "kind", "title", "activity", "archived")
    list_filter = ("record_type", "kind", "archived")
    search_fields = ("title", "documentation")
