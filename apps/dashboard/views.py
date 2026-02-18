from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import json
from apps.families.models import Family
from apps.persons.models import Person
from apps.families.models import FamilyMembership  # for role chec
from apps.activitylog.models import ActivityLog



# Utility function to check user role
def user_has_role(user, family, min_role='viewer'):
    role_hierarchy = ['viewer','member', 'admin', 'owner']
    try:
        member = FamilyMembership.objects.get(family=family, user=user)
        return role_hierarchy.index(member.role) >= role_hierarchy.index(min_role)
    except FamilyMembership.DoesNotExist:
        return False


@method_decorator(cache_page(60 * 5), name='dispatch')  # Cache dashboard for 5 minutes
class FamilyDashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/dashboard.html'

    def get(self, request, family_id):
        family = get_object_or_404(Family, id=family_id)

        # Role check: at least 'viewer' can see
        if not user_has_role(request.user, family, min_role='viewer'):
            raise PermissionDenied

        members = Person.objects.filter(family=family)

        oldest = members.exclude(birth_date__isnull=True).order_by('birth_date').first()
        youngest = members.exclude(birth_date__isnull=True).order_by('-birth_date').first()
        recent_additions = members.order_by('-created_at')[:10]
        common_surnames = (
            members.values('last_name')
            .annotate(count=Count('last_name'))
            .order_by('-count')[:5]
        )
        gender_data = members.values('gender').annotate(count=Count('id'))
        gender_labels = [x['gender'] for x in gender_data]
        gender_counts = [x['count'] for x in gender_data]
        recent_activities = (
                ActivityLog.objects
                .filter(family=family)
                .select_related('user')
                .order_by('-timestamp')[:10]
            )

        context = {
            'family': family,
            'total_members': members.count(),
            'living_count': members.filter(death_date__isnull=True).count(),
            'deceased_count': members.filter(death_date__isnull=False).count(),
            'gender_labels': json.dumps(gender_labels),
            'gender_counts': json.dumps(gender_counts),
            'oldest': oldest,
            'youngest': youngest,
            'recent_additions': recent_additions,
            'common_surnames': common_surnames,
            'recent_activities': recent_activities,
            'can_edit': user_has_role(request.user, family, min_role='owner'),
        }

        return render(request, self.template_name, context)
