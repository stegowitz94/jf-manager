from django.contrib import admin
from .models import Guardian, Leave, Member, MemberStatusHistory


class GuardianInline(admin.TabularInline):
    model = Guardian
    extra = 1
    max_num = 2


class StatusHistoryInline(admin.TabularInline):
    model = MemberStatusHistory
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("sequential_number", "last_name", "first_name", "birth_date", "activity_status", "city")
    list_filter = ("activity_status", "gender")
    search_fields = ("first_name", "last_name", "jf_card_number", "email")
    inlines = (GuardianInline, StatusHistoryInline)
    fieldsets = (
        ("Stammdaten", {"fields": (
            "sequential_number", "first_name", "last_name", "gender", "birth_date",
            "entry_date", "jf_card_number", "activity_status", "profile_image",
        )}),
        ("Kontakt", {"fields": ("street", "postal_code", "city", "phone", "mobile", "email")}),
        ("Einwilligungen", {"fields": ("photo_video_permission", "divera_permission")}),
        ("Schule und Beruf", {"fields": ("school_or_employer", "vocational_training", "career_goal", "other_organizations")}),
        ("Sensible Gesundheitsangaben", {
            "fields": ("health_notes", "swimming_status", "health_insurance"),
            "classes": ("collapse",),
            "description": "Freiwillige, besonders schützenswerte Angaben. Nur speichern, wenn sie für Betreuung und Sicherheit erforderlich sind.",
        }),
    )


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("member", "start_date", "planned_end_date", "status_after")
    list_filter = ("start_date", "planned_end_date")
    search_fields = ("member__first_name", "member__last_name")

from .models import MemberBadge
admin.site.register(MemberBadge)
