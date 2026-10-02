from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EventForm, RegisterForm, RegistrationForm
from .models import Event, Registration


# ---------- Helpers ----------
def is_organizer(user):
    return user.is_authenticated and hasattr(user, "profile") and user.profile.is_organizer


def organizer_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_organizer(request.user):
            messages.error(request, "Only organizers can open that page.")
            return redirect("event_list")
        return view(request, *args, **kwargs)

    return login_required(wrapper)


def annotated_events():
    """Events with their confirmed-registration count in a single query."""
    return Event.objects.select_related("organizer").annotate(
        confirmed=Count("registrations", filter=Q(registrations__status="confirmed"))
    )


def filter_events(params):
    """Search shared by the web page and the JSON API. Upcoming events by default."""
    events = annotated_events()
    if params.get("past") != "1":
        events = events.filter(start_time__gte=timezone.now())
    q = params.get("q", "").strip()
    if q:
        events = events.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)
        )
    return events


def serialize_event(event, request):
    return {
        "id": event.pk,
        "title": event.title,
        "location": event.location,
        "start_time": timezone.localtime(event.start_time).isoformat(),
        "capacity": event.capacity,
        "spots_left": event.spots_left,
        "is_full": event.spots_left == 0,
        "organizer": event.organizer.username,
        "url": request.build_absolute_uri(reverse("event_detail", args=[event.pk])),
    }


# ---------- Public pages ----------
def event_list(request):
    page = Paginator(filter_events(request.GET), 9).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "event_list.html", {
        "page": page,
        "querystring": params.urlencode(),
        "q": request.GET.get("q", ""),
        "show_past": request.GET.get("past") == "1",
    })


def render_detail(request, event, form=None):
    registration = None
    if request.user.is_authenticated:
        registration = Registration.objects.filter(user=request.user, event=event).first()
    return render(request, "event_detail.html", {
        "event": event,
        "registration": registration,
        "form": form or RegistrationForm(),
        "is_owner": request.user.is_authenticated and event.organizer_id == request.user.pk,
    })


def event_detail(request, pk):
    return render_detail(request, get_object_or_404(annotated_events(), pk=pk))


# ---------- Accounts ----------
def register(request):
    if request.user.is_authenticated:
        return redirect("event_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. Welcome!")
        return redirect("organizer_dashboard" if is_organizer(user) else "event_list")
    return render(request, "form_page.html", {
        "form": form, "title": "Create your account", "submit_label": "Sign up",
    })


# ---------- Attendee: register, view, cancel ----------
@login_required
@require_POST
def register_for_event(request, pk):
    event = get_object_or_404(annotated_events(), pk=pk)
    if event.is_past:
        messages.error(request, "This event has already taken place.")
        return redirect("event_detail", pk=pk)

    existing = Registration.objects.filter(user=request.user, event=event).first()
    if existing and existing.status == "confirmed":
        messages.info(request, "You are already registered for this event.")
        return redirect("event_detail", pk=pk)
    if event.spots_left <= 0:
        messages.error(request, "Sorry, this event is full.")
        return redirect("event_detail", pk=pk)

    form = RegistrationForm(request.POST)
    if not form.is_valid():
        return render_detail(request, event, form)

    with transaction.atomic():
        if existing:  # re-registering after a cancellation
            existing.phone = form.cleaned_data["phone"]
            existing.note = form.cleaned_data["note"]
            existing.status = "confirmed"
            existing.save()
        else:
            Registration.objects.create(user=request.user, event=event, **form.cleaned_data)
    messages.success(request, f"You're registered for {event.title}.")
    return redirect("my_registrations")


@login_required
def my_registrations(request):
    regs = request.user.registrations.select_related("event")
    return render(request, "my_registrations.html", {"registrations": regs})


@login_required
@require_POST
def cancel_registration(request, pk):
    reg = get_object_or_404(Registration, pk=pk, user=request.user)
    if reg.status == "confirmed":
        reg.status = "cancelled"
        reg.save(update_fields=["status"])
        messages.success(request, "Registration cancelled. Your spot was released.")
    return redirect("my_registrations")


# ---------- Organizer ----------
@organizer_required
def organizer_dashboard(request):
    events = request.user.events.annotate(
        confirmed=Count("registrations", filter=Q(registrations__status="confirmed"))
    )
    return render(request, "organizer_dashboard.html", {
        "events": events,
        "total_events": events.count(),
        "upcoming_events": events.filter(start_time__gte=timezone.now()).count(),
        "total_registrations": Registration.objects.filter(
            event__organizer=request.user, status="confirmed"
        ).count(),
    })


@organizer_required
def event_create(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.organizer = request.user
        event.save()
        messages.success(request, "Event created.")
        return redirect("organizer_dashboard")
    return render(request, "form_page.html", {
        "form": form, "title": "Create an event", "submit_label": "Create event",
    })


@organizer_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("organizer_dashboard")
    return render(request, "form_page.html", {
        "form": form, "title": "Edit event", "submit_label": "Save changes",
    })


@organizer_required
@require_POST
def event_delete(request, pk):
    get_object_or_404(Event, pk=pk, organizer=request.user).delete()
    messages.success(request, "Event deleted.")
    return redirect("organizer_dashboard")


@organizer_required
def event_attendees(request, pk):
    event = get_object_or_404(annotated_events(), pk=pk, organizer=request.user)
    regs = event.registrations.select_related("user")
    return render(request, "event_attendees.html", {
        "event": event,
        "attendees": regs.filter(status="confirmed"),
        "cancelled_count": regs.filter(status="cancelled").count(),
    })


# ---------- JSON API ----------
def api_events(request):
    events = [serialize_event(e, request) for e in filter_events(request.GET)[:50]]
    return JsonResponse({"count": len(events), "results": events})


def api_event_detail(request, pk):
    event = get_object_or_404(annotated_events(), pk=pk)
    data = serialize_event(event, request)
    data["description"] = event.description
    return JsonResponse(data)


def api_my_registrations(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)
    regs = request.user.registrations.select_related("event")
    return JsonResponse({"results": [
        {
            "registration_id": r.pk,
            "event": r.event.title,
            "event_id": r.event_id,
            "start_time": timezone.localtime(r.event.start_time).isoformat(),
            "status": r.status,
            "registered_at": r.created_at.isoformat(),
        }
        for r in regs
    ]})
