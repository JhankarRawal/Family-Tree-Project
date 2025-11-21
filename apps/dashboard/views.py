# apps/dashboard/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.families.models import FamilyMembership, JoinRequest
from apps.persons.models import Person
from django.db.models import Count
import json

class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get memberships
        memberships = FamilyMembership.objects.filter(user=user)
        families = [m.family for m in memberships]
        family_roles = {m.family.id: m.role for m in memberships}

        family_stats = {}
        chart_data = {}
        for family in families:
            people = Person.objects.filter(family=family)
            stats = {
                'total_people': people.count(),
                'living': people.filter(is_living=True).count(),
                'deceased': people.filter(is_living=False).count(),
                'male': people.filter(gender='M').count(),
                'female': people.filter(gender='F').count(),
            }
            family_stats[family.id] = stats
            chart_data[family.id] = {
                'labels': ['Male', 'Female', 'Living', 'Deceased'],
                'values': [stats['male'], stats['female'], stats['living'], stats['deceased']],
            }

        # Pending join requests for owner/admin
        pending_requests = JoinRequest.objects.filter(
            family__in=families,
            approved__isnull=True,  # pending
            family__memberships__user=user,
            family__memberships__role__in=['owner', 'admin']
        ).select_related('user', 'family')

        context.update({
            'families': families,
            'family_roles': family_roles,
            'family_stats': family_stats,
            'chart_data': chart_data,
            'pending_requests': pending_requests,
        })
        return context
