# Task 2: Event Registration System

CodeAlpha Backend Development Internship project built with **Django**, **SQLite** and **Tailwind CSS**.

## Features
- Sign up as an **attendee** or an **organizer** (tick "I want to organize events")
- Attendees: search events, register with a phone number and optional note, view and cancel their registrations, re-register after cancelling
- Organizers: create, edit and delete events, see the attendee list for each event, dashboard with counts
- Capacity handling: spots left are shown, full events cannot be booked, cancelling releases the spot
- Duplicate registrations and registrations for past events are blocked
- Django admin panel for all models
- JSON API endpoints

## Setup
```bash
cd task2_event_registration
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo   # optional: demo accounts and sample events
python manage.py runserver
```
Open http://127.0.0.1:8000

Demo logins (after `seed_demo`): `demo_organizer` / `demo12345` and `demo_attendee` / `demo12345`.

Admin panel: `python manage.py createsuperuser`, then open http://127.0.0.1:8000/admin

Tailwind CSS is loaded from the Tailwind CDN in `events/templates/base.html`, so an internet connection is needed to see the styling.

## Pages and endpoints
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Event list with search (`?q=`, `?past=1`) |
| GET | `/events/<id>/` | Event details and registration form |
| POST | `/events/<id>/register/` | Submit a registration (login required) |
| POST | `/registrations/<id>/cancel/` | Cancel your registration |
| GET | `/my-registrations/` | Your registrations |
| GET | `/organizer/` | Organizer dashboard |

## JSON API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events/?q=` | Upcoming events with spots left (add `past=1` for past ones) |
| GET | `/api/events/<id>/` | Event details |
| GET | `/api/my-registrations/` | Logged-in user's registrations |

## Project structure
```
task2_event_registration/
  manage.py
  eventsite/           project settings and root urls
  events/
    models.py          Profile, Event, Registration
    views.py           pages, registration logic, JSON API
    forms.py
    urls.py
    admin.py
    templates/         Tailwind HTML templates
    management/commands/seed_demo.py
```
