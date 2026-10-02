from django import template

register = template.Library()

BADGES = {
    "applied": "bg-slate-200 text-slate-700",
    "reviewing": "bg-sky-200 text-sky-800",
    "shortlisted": "bg-amber-200 text-amber-800",
    "rejected": "bg-rose-200 text-rose-800",
    "hired": "bg-emerald-200 text-emerald-800",
}


@register.filter
def status_badge(status):
    return BADGES.get(status, BADGES["applied"])
