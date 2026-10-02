from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_organizer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({'organizer' if self.is_organizer else 'attendee'})"


class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(
        default=50, validators=[MinValueValidator(1)], help_text="Maximum number of attendees"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title

    @property
    def confirmed_count(self):
        if hasattr(self, "confirmed"):  # set by the annotated queryset (avoids extra queries)
            return self.confirmed
        return self.registrations.filter(status="confirmed").count()

    @property
    def spots_left(self):
        return max(self.capacity - self.confirmed_count, 0)

    @property
    def is_past(self):
        return self.start_time < timezone.now()


class Registration(models.Model):
    STATUS = [("confirmed", "Confirmed"), ("cancelled", "Cancelled")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registrations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    phone = models.CharField(max_length=30)
    note = models.TextField(blank=True, help_text="Optional, e.g. dietary needs or questions")
    status = models.CharField(max_length=10, choices=STATUS, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.status})"
