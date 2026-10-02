from django.contrib import admin

from .models import Application, Candidate, Employer, Job, Notification, Resume


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "website")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "headline")


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "candidate", "uploaded_at")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "location", "job_type", "is_open", "created_at")
    list_filter = ("job_type", "is_open")
    search_fields = ("title", "description", "location")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "applied_at")
    list_filter = ("status",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
