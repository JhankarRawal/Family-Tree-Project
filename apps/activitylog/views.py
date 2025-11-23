# activity/views.py
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from apps.families.models import Family
from .models import ActivityLog

class ActivityListView(ListView):
    template_name = "activitylog/log_list.html"
    context_object_name = "logs"

    def get_queryset(self):
        family = get_object_or_404(Family, id=self.kwargs["family_id"])

        # Permission check
        membership = family.memberships.filter(user=self.request.user).first()
        if not membership or membership.role not in ("owner", "admin"):
            return ActivityLog.objects.none()

        return ActivityLog.objects.filter(family=family)
