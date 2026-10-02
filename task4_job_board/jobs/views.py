import os
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ApplicationForm, JobForm, RegisterForm, ResumeForm
from .models import Application, Job, Notification, Resume


# ---------- Helpers ----------
def role_required(role):
    """Allow only users that have an Employer or Candidate profile."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, role):
                messages.error(request, f"That page is only available to {role}s.")
                return redirect("job_list")
            return view(request, *args, **kwargs)

        return login_required(wrapper)

    return decorator


employer_required = role_required("employer")
candidate_required = role_required("candidate")


def notify(user, message, link=""):
    Notification.objects.create(user=user, message=message, link=link)


def filter_jobs(params):
    """Search + filters shared by the web page and the JSON API."""
    jobs = Job.objects.filter(is_open=True).select_related("employer")
    q = params.get("q", "").strip()
    if q:
        jobs = jobs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(employer__company_name__icontains=q)
        )
    location = params.get("location", "").strip()
    if location:
        jobs = jobs.filter(location__icontains=location)
    job_type = params.get("type", "")
    if job_type in dict(Job.JOB_TYPES):
        jobs = jobs.filter(job_type=job_type)
    return jobs


def serialize_job(job, request):
    return {
        "id": job.pk,
        "title": job.title,
        "company": job.employer.company_name,
        "location": job.location,
        "job_type": job.job_type,
        "salary": job.salary,
        "is_open": job.is_open,
        "posted": job.created_at.date().isoformat(),
        "url": request.build_absolute_uri(reverse("job_detail", args=[job.pk])),
    }


# ---------- Public pages ----------
def job_list(request):
    page = Paginator(filter_jobs(request.GET), 9).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "job_list.html", {
        "page": page,
        "querystring": params.urlencode(),
        "job_types": Job.JOB_TYPES,
        "q": request.GET.get("q", ""),
        "location": request.GET.get("location", ""),
        "selected_type": request.GET.get("type", ""),
    })


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related("employer"), pk=pk)
    user = request.user
    already_applied = hasattr(user, "candidate") and Application.objects.filter(
        job=job, candidate=user.candidate
    ).exists()
    is_owner = hasattr(user, "employer") and job.employer_id == user.employer.pk
    return render(request, "job_detail.html", {
        "job": job, "already_applied": already_applied, "is_owner": is_owner,
    })


# ---------- Accounts ----------
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. Welcome!")
        return redirect("dashboard")
    return render(request, "form_page.html", {
        "form": form, "title": "Create your account", "submit_label": "Sign up",
    })


@login_required
def dashboard(request):
    user = request.user
    if hasattr(user, "employer"):
        jobs = user.employer.jobs.annotate(app_count=Count("applications"))
        applications = Application.objects.filter(job__employer=user.employer)
        return render(request, "dashboard_employer.html", {
            "jobs": jobs,
            "total_jobs": jobs.count(),
            "open_jobs": jobs.filter(is_open=True).count(),
            "total_applications": applications.count(),
            "new_applications": applications.filter(status="applied").count(),
        })
    if hasattr(user, "candidate"):
        applications = user.candidate.applications.select_related("job", "job__employer", "resume")
        return render(request, "dashboard_candidate.html", {"applications": applications})
    return redirect("job_list")


@login_required
def notifications_view(request):
    items = list(Notification.objects.filter(user=request.user)[:50])
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, "notifications.html", {"items": items})


# ---------- Candidate: resumes and applications ----------
@candidate_required
def resumes(request):
    candidate = request.user.candidate
    form = ResumeForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        resume = form.save(commit=False)
        resume.candidate = candidate
        resume.save()
        messages.success(request, "Resume uploaded.")
        return redirect("resumes")
    return render(request, "resumes.html", {"form": form, "resumes": candidate.resumes.all()})


@candidate_required
@require_POST
def resume_delete(request, pk):
    resume = get_object_or_404(Resume, pk=pk, candidate=request.user.candidate)
    if resume.applications.exists():
        messages.error(request, "This resume is attached to an application, so it can't be deleted.")
    else:
        resume.file.delete(save=False)
        resume.delete()
        messages.success(request, "Resume deleted.")
    return redirect("resumes")


@login_required
def resume_download(request, pk):
    """Only the owner, an employer who received it, or staff can download."""
    resume = get_object_or_404(Resume, pk=pk)
    user = request.user
    allowed = (
        user.is_staff
        or resume.candidate.user_id == user.pk
        or (
            hasattr(user, "employer")
            and Application.objects.filter(resume=resume, job__employer=user.employer).exists()
        )
    )
    if not allowed:
        raise PermissionDenied
    return FileResponse(
        resume.file.open("rb"), as_attachment=True, filename=os.path.basename(resume.file.name)
    )


@candidate_required
def apply(request, pk):
    job = get_object_or_404(Job, pk=pk, is_open=True)
    candidate = request.user.candidate
    if Application.objects.filter(job=job, candidate=candidate).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect("dashboard")
    if not candidate.resumes.exists():
        messages.error(request, "Upload a resume first, then apply.")
        return redirect("resumes")

    form = ApplicationForm(request.POST or None, candidate=candidate)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.candidate = candidate
        application.save()
        notify(
            job.employer.user,
            f"{candidate.full_name} applied for {job.title}.",
            reverse("job_applicants", args=[job.pk]),
        )
        messages.success(request, "Application submitted.")
        return redirect("dashboard")
    return render(request, "form_page.html", {
        "form": form,
        "title": f"Apply for {job.title}",
        "subtitle": job.employer.company_name,
        "submit_label": "Submit application",
    })


# ---------- Employer: jobs and applicants ----------
@employer_required
def job_create(request):
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.employer = request.user.employer
        job.save()
        messages.success(request, "Job posted.")
        return redirect("dashboard")
    return render(request, "form_page.html", {
        "form": form, "title": "Post a job", "submit_label": "Post job",
    })


@employer_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user.employer)
    form = JobForm(request.POST or None, instance=job)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Job updated.")
        return redirect("dashboard")
    return render(request, "form_page.html", {
        "form": form, "title": "Edit job", "submit_label": "Save changes",
    })


@employer_required
@require_POST
def job_delete(request, pk):
    get_object_or_404(Job, pk=pk, employer=request.user.employer).delete()
    messages.success(request, "Job deleted.")
    return redirect("dashboard")


@employer_required
def job_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user.employer)
    applications = job.applications.select_related("candidate", "candidate__user", "resume")
    return render(request, "job_applicants.html", {
        "job": job, "applications": applications, "status_choices": Application.STATUS,
    })


@employer_required
@require_POST
def update_status(request, pk):
    application = get_object_or_404(
        Application.objects.select_related("job", "candidate__user"),
        pk=pk, job__employer=request.user.employer,
    )
    new_status = request.POST.get("status")
    labels = dict(Application.STATUS)
    if new_status in labels and new_status != application.status:
        application.status = new_status
        application.save(update_fields=["status"])
        notify(
            application.candidate.user,
            f'Your application for {application.job.title} is now "{labels[new_status]}".',
            reverse("dashboard"),
        )
        messages.success(request, "Status updated and the candidate was notified.")
    return redirect("job_applicants", pk=application.job_id)


# ---------- JSON API ----------
def api_jobs(request):
    jobs = filter_jobs(request.GET)[:50]
    results = [serialize_job(j, request) for j in jobs]
    return JsonResponse({"count": len(results), "results": results})


def api_job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related("employer"), pk=pk)
    data = serialize_job(job, request)
    data["description"] = job.description
    return JsonResponse(data)


def api_my_applications(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)
    if not hasattr(request.user, "candidate"):
        return JsonResponse({"error": "Only candidates have applications"}, status=403)
    apps = request.user.candidate.applications.select_related("job", "job__employer")
    return JsonResponse({"results": [
        {
            "job": a.job.title,
            "company": a.job.employer.company_name,
            "status": a.status,
            "status_label": a.get_status_display(),
            "applied_at": a.applied_at.isoformat(),
        }
        for a in apps
    ]})
