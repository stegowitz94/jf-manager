from django.contrib import admin
from .models import AppSettings, ExternalLink, DashboardPreference
from .image_utils import optimize_profile_image

@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Allgemein", {"fields": ("organisation_name", "short_name", "logo", "notification_recipients")}),
        ("Benachrichtigungen", {"fields": ("birthday_notifications", "absence_notifications", "leave_notifications", "unexcused_threshold", "excused_threshold", "leave_notice_days")}),
        ("Schnupperdienst", {"fields": ("scouting_age_years", "scouting_lead_months", "scouting_reminder_days")}),
    )

    def save_model(self, request, obj, form, change):
        if "logo" in form.changed_data and obj.logo:
            old_name = None
            if change:
                try: old_name = AppSettings.objects.get(pk=obj.pk).logo.name
                except AppSettings.DoesNotExist: pass
            obj.logo = optimize_profile_image(obj.logo, stem="organisation-logo")
            super().save_model(request, obj, form, change)
            if old_name and old_name != obj.logo.name:
                obj.logo.storage.delete(old_name)
            return
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return not AppSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display=("name","category","visible","favorite","order")
    list_editable=("visible","favorite","order")
    list_filter=("category","visible","favorite")

@admin.register(DashboardPreference)
class DashboardPreferenceAdmin(admin.ModelAdmin):
    list_display=("user","show_member_counts","show_gender_chart","show_status_chart","show_waiting_list")
