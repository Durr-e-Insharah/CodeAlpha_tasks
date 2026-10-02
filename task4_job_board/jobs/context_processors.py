def nav_context(request):
    user = request.user
    if not user.is_authenticated:
        return {}
    return {
        "unread_count": user.notifications.filter(is_read=False).count(),
        "is_employer": hasattr(user, "employer"),
        "is_candidate": hasattr(user, "candidate"),
    }
