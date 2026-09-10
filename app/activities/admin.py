from django.contrib import admin

from .models import Activity, Attendance, SupervisorAttendance, ActivityTypeSetting


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0


class SupervisorAttendanceInline(admin.TabularInline):
    model = SupervisorAttendance
    extra = 0


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("starts_at", "title", "activity_type", "attendance_completed")
    list_filter = ("activity_type", "attendance_completed")
    search_fields = ("title", "location")
    inlines = (AttendanceInline, SupervisorAttendanceInline)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("activity", "member", "status", "source", "updated_at")
    list_filter = ("status", "source")
    search_fields = ("member__first_name", "member__last_name", "activity__title")


@admin.register(SupervisorAttendance)
class SupervisorAttendanceAdmin(admin.ModelAdmin):
    list_display = ("activity", "supervisor", "status", "source", "updated_at")
    list_filter = ("status", "source")
    search_fields = ("supervisor__first_name", "supervisor__last_name", "activity__title")


@admin.register(ActivityTypeSetting)
class ActivityTypeSettingAdmin(admin.ModelAdmin):
    list_display = ("activity_type", "default_start_time", "default_end_time")
    list_editable = ("default_start_time", "default_end_time")
    ordering = ("activity_type",)
