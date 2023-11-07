from django.contrib import admin

from .models import Appointment, AppointmentCategory, AppointmentType, Notification


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    list_display = ("creation_date", "start_time", "end_time", "date")
    list_filter = ("creation_date", "date")
    # raw_id_fields = ("appointment_type",)
    autocomplete_fields = ("appointment_type",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "creation_date",
        "last_sent",
        "minimum_waittime",
    )
    list_filter = ("creation_date", "last_sent")
    autocomplete_fields = ("appointment_type",)


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "index", "appointment_category")
    list_filter = ("appointment_category",)
    search_fields = ("name",)


@admin.register(AppointmentCategory)
class AppointmentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "index")
    search_fields = ("name",)
