from django.urls import path
from .views import  FamilyDashboardView

app_name = "dashboard"

urlpatterns = [
    path('<int:family_id>/',  FamilyDashboardView.as_view(), name='family_dashboard'),
]