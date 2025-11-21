from django.urls import path
from .views import (
    PersonListView, PersonCreateView, PersonDetailView,
    PersonUpdateView, PersonDeleteView
)
app_name = 'persons'

urlpatterns = [
    path("", PersonListView.as_view(), name="list"),
    path("add/", PersonCreateView.as_view(), name="person_add"),
    path("<int:person_id>/", PersonDetailView.as_view(), name="person_detail"),
    path("<int:person_id>/edit/", PersonUpdateView.as_view(), name="person_edit"),
    path("<int:person_id>/delete/", PersonDeleteView.as_view(), name="person_delete"),
]