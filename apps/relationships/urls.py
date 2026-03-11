from django.urls import path
from .views import *

app_name = "relationships"

urlpatterns = [
    path("<int:person_id>/add-parent/", AddParentView.as_view(), name="add_parent"),
    path("<int:person_id>/add-child/", AddChildView.as_view(), name="add_child"),
    path("<int:person_id>/add-spouse/", AddSpouseView.as_view(), name="add_spouse"),
    path("delete/<int:rel_id>/", RelationshipDeleteView.as_view(), name="delete"),

    path("relationship-check/", relationship_check_page, name='relationship_check_page'),
    path("relationship-check/api/<int:person_a_id>/<int:person_b_id>/", relationship_check_api, name='relationship_check_api'),
]