from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def validate_resume_size(file):
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Resume must be 5 MB or smaller.")


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employer")
    company_name = models.CharField(max_length=150)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company_name


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="candidate")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    headline = models.CharField(max_length=150, blank=True)
    skills = models.CharField(max_length=250, blank=True, help_text="Comma separated, e.g. Python, Django, SQL")

    def __str__(self):
        return self.full_name


class Resume(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=100)
    file = models.FileField(
        upload_to="resumes/",
        validators=[FileExtensionValidator(["pdf", "doc", "docx"]), validate_resume_size],
        help_text="PDF, DOC or DOCX, up to 5 MB.",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


class Job(models.Model):
    JOB_TYPES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default="full_time")
    salary = models.CharField(max_length=80, blank=True, help_text="Optional, e.g. PKR 80,000 - 120,000")
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} at {self.employer}"


class Application(models.Model):
    STATUS = [
        ("applied", "Applied"),
        ("reviewing", "Under review"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, related_name="applications")
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="applied")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ("job", "candidate")

    def __str__(self):
        return f"{self.candidate} -> {self.job}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message
