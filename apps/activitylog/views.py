# activity/views.py
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from apps.families.models import Family,FamilyMembership
from .models import ActivityLog
from django.core.exceptions import PermissionDenied


def user_has_role(user, family, min_role='viewer'):
    role_hierarchy = ['viewer', 'editor', 'admin', 'owner']
    try:
        member = FamilyMembership.objects.get(family=family, user=user)
        return role_hierarchy.index(member.role) >= role_hierarchy.index(min_role)
    except FamilyMembership.DoesNotExist:
        return False


class ActivityListView(ListView):
    model = ActivityLog
    template_name = "activitylog/log_list.html"
    context_object_name = "activities"
    paginate_by = 20

    def get_queryset(self):
        self.family = get_object_or_404(Family, id=self.kwargs["family_id"])

        if not user_has_role(self.request.user, self.family, "viewer"):
            raise PermissionDenied

        qs = (
            ActivityLog.objects
            .filter(family=self.family)
            .select_related("user")
            .order_by("-timestamp")
        )

        # -------- FILTERS --------
        action_type = self.request.GET.get("action_type")
        target_type = self.request.GET.get("target_type")
        user_id = self.request.GET.get("user")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if action_type:
            qs = qs.filter(action_type=action_type)

        if target_type:
            qs = qs.filter(target_type=target_type)

        if user_id:
            qs = qs.filter(user_id=user_id)

        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)

        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["family"] = self.family

        context["users"] = (
            ActivityLog.objects
            .filter(family=self.family, user__isnull=False)
            .values("user__id", "user__username")
            .distinct()
        )

        context["filters"] = self.request.GET
        return context
