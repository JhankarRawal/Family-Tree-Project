from django.urls import path
from django.http import HttpResponse

def person_search(request): return HttpResponse("Person search")

app_name = 'search'

urlpatterns = [
    path('', person_search, name='person_search'),
]
