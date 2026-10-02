from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event, Profile

EVENTS = [
    ("Python for Beginners Workshop", "Wah Cantt", 3, 40, "A hands-on introduction to Python. Bring your laptop and we will build a small project together."),
    ("Django Meetup", "Islamabad", 10, 60, "Talks and networking for Django developers. Lightning talks are welcome."),
    ("Career Fair 2026", "Rawalpindi", 14, 200, "Meet hiring teams from software companies and get your CV reviewed."),
    ("Intro to Git and GitHub", "Online", 5, 100, "Learn commits, branches and pull requests, and publish your first repository."),
    ("Hackathon Kickoff", "Lahore", 20, 3, "A tiny kickoff session with only a few seats, so you can test the full-event message."),
    ("Resume Writing Session", "Online", 7, 30, "Practical tips to write a clear one-page CV for internships and entry-level jobs."),
]


class Command(BaseCommand):
    help = "Create demo accounts and sample events for testing and screen recordings."

    def handle(self, *args, **options):
        org, created = User.objects.get_or_create(username="demo_organizer", defaults={"email": "organizer@example.com"})
        if created:
            org.set_password("demo12345")
            org.save()
        Profile.objects.get_or_create(user=org, defaults={"is_organizer": True})

        att, created = User.objects.get_or_create(username="demo_attendee", defaults={"email": "attendee@example.com"})
        if created:
            att.set_password("demo12345")
            att.save()
        Profile.objects.get_or_create(user=att, defaults={"is_organizer": False})

        for title, location, days, capacity, description in EVENTS:
            Event.objects.get_or_create(
                organizer=org, title=title,
                defaults={
                    "location": location,
                    "capacity": capacity,
                    "description": description,
                    "start_time": (timezone.now() + timedelta(days=days)).replace(hour=15, minute=0, second=0, microsecond=0),
                },
            )
        self.stdout.write(self.style.SUCCESS(
            "Demo data ready. Logins: demo_organizer / demo12345 and demo_attendee / demo12345"
        ))
