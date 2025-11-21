from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from apps.families.models import Family

class FamilyPermissionMixin:
    """Checks membership role and attaches `self.family` to the view."""

    allowed_roles = []  # Define in views

    def dispatch(self, request, *args, **kwargs):
        family_id = kwargs.get("pk")
        self.family = get_object_or_404(Family, pk=family_id)

        membership = self.family.memberships.filter(user=request.user).first()

        # Restrict access
        if not membership:
            raise PermissionDenied("You are not a member of this family.")

        if self.allowed_roles and membership.role not in self.allowed_roles:
            raise PermissionDenied("You do not have permission.")

        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["family"] = self.family  # <-- FIX: inject family
        return context
