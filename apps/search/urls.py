from django.urls import path
from .views import (
    PersonSearchView,
    PersonFilterView,
    PersonAutocompleteView,
    RelationshipPathView,
    AncestorsView,
)

app_name = "search"

urlpatterns = [
    path("<int:family_id>/persons/", PersonSearchView.as_view(), name="person_search"),
    path("<int:family_id>/filters/", PersonFilterView.as_view(), name="filters"),
    path("<int:family_id>/autocomplete/", PersonAutocompleteView.as_view(), name="autocomplete"),
    path("<int:family_id>/path/<int:start_id>/<int:end_id>/", RelationshipPathView.as_view(), name="path"),
    path("<int:family_id>/person/<int:person_id>/relations/", AncestorsView.as_view(), name="person_relations"),
]
