from django.contrib import admin

from .models import Supervisor, SupervisorFunction


@admin.register(SupervisorFunction)
class SupervisorFunctionAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "active")
    list_editable = ("sort_order", "active")


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ("sequential_number", "last_name", "first_name", "activity_status", "email")
    list_filter = ("activity_status", "functions")
    search_fields = ("first_name", "last_name", "email", "phone", "mobile")
    filter_horizontal = ("functions",)

from .models import SupervisorTraining
admin.site.register(SupervisorTraining)
