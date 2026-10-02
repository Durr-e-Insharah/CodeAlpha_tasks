from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    # Public pages
    path("", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),

    # Accounts
    path("register/", views.register, name="register"),
    path(
        "login/",
        LoginView.as_view(
            template_name="form_page.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
            extra_context={"title": "Log in", "submit_label": "Log in"},
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("notifications/", views.notifications_view, name="notifications"),

    # Candidate
    path("jobs/<int:pk>/apply/", views.apply, name="apply"),
    path("resumes/", views.resumes, name="resumes"),
    path("resumes/<int:pk>/delete/", views.resume_delete, name="resume_delete"),
    path("resumes/<int:pk>/download/", views.resume_download, name="resume_download"),

    # Employer
    path("employer/jobs/new/", views.job_create, name="job_create"),
    path("employer/jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("employer/jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    path("employer/jobs/<int:pk>/applicants/", views.job_applicants, name="job_applicants"),
    path("employer/applications/<int:pk>/status/", views.update_status, name="update_status"),

    # JSON API
    path("api/jobs/", views.api_jobs, name="api_jobs"),
    path("api/jobs/<int:pk>/", views.api_job_detail, name="api_job_detail"),
    path("api/my-applications/", views.api_my_applications, name="api_my_applications"),
]
