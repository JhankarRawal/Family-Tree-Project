from django.http import JsonResponse
from apps.persons.models import Person
from django.db.models import Count

def family_dashboard_api(request, id):
    members = Person.objects.filter(family_id=id)
    data = {
    'total': members.count(),
    'living': members.filter(date_of_death__isnull=True).count(),
    'deceased': members.filter(date_of_death__isnull=False).count(),
    'gender': list(members.values('gender').annotate(count=Count('id'))),
    }
    return JsonResponse(data)