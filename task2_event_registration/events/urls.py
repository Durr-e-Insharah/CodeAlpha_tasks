from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    # Public
    path("", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),

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

    # Attendee: registrations
    path("events/<int:pk>/register/", views.register_for_event, name="register_for_event"),
    path("my-registrations/", views.my_registrations, name="my_registrations"),
    path("registrations/<int:pk>/cancel/", views.cancel_registration, name="cancel_registration"),

    # Organizer
    path("organizer/", views.organizer_dashboard, name="organizer_dashboard"),
    path("organizer/events/new/", views.event_create, name="event_create"),
    path("organizer/events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("organizer/events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("organizer/events/<int:pk>/attendees/", views.event_attendees, name="event_attendees"),

    # JSON API
    path("api/events/", views.api_events, name="api_events"),
    path("api/events/<int:pk>/", views.api_event_detail, name="api_event_detail"),
    path("api/my-registrations/", views.api_my_registrations, name="api_my_registrations"),
]
