from django.urls import path
from .views import *

app_name = "relationships"

urlpatterns = [
    path("<int:family_id>/<int:person_id>/add-parent/", AddParentView.as_view(), name="add_parent"),
    path("<int:family_id>/<int:person_id>/add-child/", AddChildView.as_view(), name="add_child"),
    path("<int:family_id>/<int:person_id>/add-spouse/", AddSpouseView.as_view(), name="add_spouse"),
    path("<int:family_id>/delete/<int:rel_id>/", RelationshipDeleteView.as_view(), name="delete"),
]
