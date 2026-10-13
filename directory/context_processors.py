def coffee_user_role(request):
    """Expose a safe, display-only role label to templates. Views enforce permissions."""
    user = getattr(request, "user", None)
    role = "guest"
    if user is not None and user.is_authenticated:
        if user.is_superuser or user.is_staff:
            role = "admin"
        else:
            from .models import UserProfile
            role = UserProfile.objects.filter(user_id=user.pk).values_list("role", flat=True).first() or "buyer"
    return {"coffee_user_role": role}
