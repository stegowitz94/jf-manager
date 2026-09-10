from django.contrib import admin
from .models import WaitingListEntry
@admin.register(WaitingListEntry)
class WaitingListEntryAdmin(admin.ModelAdmin):
    list_display=("last_name","first_name","city","status","created_at")
    list_filter=("status","city")
    search_fields=("first_name","last_name","phone","email","city")
