from django.contrib import admin
from .models import NotificationLog, PushSubscription, UserNotificationPreference
@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display=("created_at","notification_type","subject","status")
    list_filter=("notification_type","status")
    search_fields=("subject","recipients","event_key")
    readonly_fields=("event_key","notification_type","subject","recipients","status","error","created_at")
    def has_add_permission(self,request): return False


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display=("user","created_at","last_seen_at")
    search_fields=("user__username","endpoint")
    readonly_fields=("endpoint","p256dh","auth","user_agent","created_at","last_seen_at")

@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display=("user","email_enabled","push_enabled","birthdays","absences","leave_end","upcoming_activity")
