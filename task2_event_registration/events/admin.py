from django.contrib import admin

from .models import Event, Profile, Registration


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_organizer")
    list_filter = ("is_organizer",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "location", "start_time", "capacity")
    search_fields = ("title", "location", "description")
    list_filter = ("start_time",)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "created_at")
    list_filter = ("status", "event")
