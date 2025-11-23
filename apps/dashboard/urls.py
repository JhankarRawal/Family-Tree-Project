from django.urls import path
from .views import UserDashboardView

app_name = "dashboard"

urlpatterns = [
    path('<int:family_id>/', UserDashboardView.as_view(), name='dashboard'),
]