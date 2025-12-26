from django.urls import path
from .views import FamilyTreeView, CenteredTreeView, TreeDataAPIView

app_name = "tree_per_family"
urlpatterns = [
    path("", FamilyTreeView.as_view(), name="view"),
    path("<int:person_id>/", CenteredTreeView.as_view(), name="tree_centered"),
    path("api/<int:person_id>/", TreeDataAPIView.as_view(), name="tree_data"),
]
