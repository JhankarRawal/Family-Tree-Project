from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import FamilyMember

def family_role_required(min_role='viewer'):
    role_hierarchy = ['viewer', 'editor', 'admin', 'owner']
    def decorator(view_func):
        def _wrapped_view(request, family_id, *args, **kwargs):
            member = get_object_or_404(FamilyMember, family_id=family_id, user=request.user)
            if role_hierarchy.index(member.role) < role_hierarchy.index(min_role):
                return HttpResponseForbidden("You do not have permission to perform this action.")
            return view_func(request, family_id, *args, **kwargs)
        return _wrapped_view
    return decorator
