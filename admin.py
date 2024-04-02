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
        "creation_date",
        "start_time",
        "end_time",
        "date",
        "location",
    )
    list_filter = ("creation_date", "date")
    autocomplete_fields = ("appointment_type",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "language",
        "creation_date",
        "last_sent",
        "minimum_waittime",
        "active",
    )
    list_filter = ("creation_date", "last_sent", "active")
    autocomplete_fields = ("appointment_type",)


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "index", "active", "appointment_category")
    list_filter = ("active", "appointment_category")
    autocomplete_fields = ("location",)
    search_fields = ("name",)


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
