from django.urls import path
from .views import ActivityListView

app_name = "activitylog"

urlpatterns = [
    path("<int:family_id>/logs/", ActivityListView.as_view(), name="logs"),
]