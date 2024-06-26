from django.contrib import admin

from .models import (
    Appointment,
    AppointmentCategory,
    AppointmentType,
    Department,
    Location,
    Notification,
    ScraperRun,
)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    list_display = (
        "start_time",
        "end_time",
        "date",
        "location",
        "appointment_type",
    )
    list_filter = ("date", "location", "appointment_type", "start_time", "end_time")
    autocomplete_fields = ("appointment_type", "location")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "language",
        "creation_date",
        "last_sent",
        "minimum_waittime",
        "active",
        "confirmed",
    )
    list_filter = ("creation_date", "last_sent", "active")
    autocomplete_fields = ("appointment_type",)
    actions = [
        "activate_action",
        "deactivate_action",
        "confirm_action",
        "unconfirm_action",
    ]

    def activate_action(self, request, queryset):
        updated_rows = queryset.update(active=True)
        self.message_user(request, f"{updated_rows} Benachrichtigungen aktiviert.")

    activate_action.short_description = "Benachrichtigungen aktivieren"

    def deactivate_action(self, request, queryset):
        updated_rows = queryset.update(active=False)
        self.message_user(request, f"{updated_rows} Benachrichtigungen deaktiviert.")

    deactivate_action.short_description = "Benachrichtigungen deaktivieren"

    def confirm_action(self, request, queryset):
        updated_rows = queryset.update(confirmed=True)
        self.message_user(
            request, f"{updated_rows} Benachrichtigungs E-Mails bestätigt."
        )

    confirm_action.short_description = "E-Mails bestätigen"

    def unconfirm_action(self, request, queryset):
        updated_rows = queryset.update(confirmed=False)
        self.message_user(
            request, f"{updated_rows} Benachrichtigungs E-Mails deaktiviert."
        )

    unconfirm_action.short_description = "E-Mails deaktivieren"


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "index", "active", "appointment_category")
    list_filter = ("active", "appointment_category")
    autocomplete_fields = ("location",)
    search_fields = ("name",)
    actions = ["activate_action", "deactivate_action"]

    def activate_action(self, request, queryset):
        updated_rows = queryset.update(active=True)
        self.message_user(request, f"{updated_rows} Anliegen aktiviert.")

    activate_action.short_description = "Anliegen aktivieren"

    def deactivate_action(self, request, queryset):
        updated_rows = queryset.update(active=False)
        self.message_user(request, f"{updated_rows} Anliegen deaktiviert.")

    deactivate_action.short_description = "Anliegen deaktivieren"


@admin.register(AppointmentCategory)
class AppointmentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "index", "department")
    list_filter = ("department",)
    search_fields = ("name",)


@admin.register(ScraperRun)
class ScraperRunAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time")
    list_filter = ("start_time", "end_time")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "descriptor", "index")
    search_fields = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "index")
    search_fields = ("name",)
