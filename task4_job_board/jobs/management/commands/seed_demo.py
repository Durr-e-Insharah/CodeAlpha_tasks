from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from jobs.models import Candidate, Employer, Job

JOBS = [
    ("Junior Python Developer", "Lahore", "full_time", "PKR 90,000 - 130,000",
     "Build and maintain backend services in Python and Django. You will write clean, tested code and work closely with the product team."),
    ("Backend Intern", "Remote", "internship", "Stipend",
     "Learn by building real APIs with Django. Ideal for students who know Python basics and want hands-on experience."),
    ("Django REST Engineer", "Islamabad", "contract", "PKR 150,000 - 200,000",
     "Design REST APIs, write database models and improve performance of an existing Django application."),
    ("Data Entry Specialist", "Rawalpindi", "part_time", "PKR 40,000",
     "Maintain accurate records in our internal systems. Attention to detail is the key skill for this role."),
    ("QA Engineer", "Karachi", "full_time", "PKR 100,000 - 140,000",
     "Plan and run manual and automated tests for web applications, and report bugs clearly to developers."),
    ("Technical Writer", "Remote", "part_time", "",
     "Write clear documentation, tutorials and API guides for developers who use our products."),
]


class Command(BaseCommand):
    help = "Create demo accounts and sample jobs for testing and screen recordings."

    def handle(self, *args, **options):
        boss, created = User.objects.get_or_create(username="demo_employer", defaults={"email": "employer@example.com"})
        if created:
            boss.set_password("demo12345")
            boss.save()
        employer, _ = Employer.objects.get_or_create(user=boss, defaults={"company_name": "Northwind Tech"})

        seeker, created = User.objects.get_or_create(username="demo_candidate", defaults={"email": "candidate@example.com"})
        if created:
            seeker.set_password("demo12345")
            seeker.save()
        Candidate.objects.get_or_create(user=seeker, defaults={"full_name": "Demo Candidate"})

        for title, location, job_type, salary, description in JOBS:
            Job.objects.get_or_create(
                employer=employer, title=title,
                defaults={"location": location, "job_type": job_type, "salary": salary, "description": description},
            )
        self.stdout.write(self.style.SUCCESS(
            "Demo data ready. Logins: demo_employer / demo12345 and demo_candidate / demo12345"
        ))
