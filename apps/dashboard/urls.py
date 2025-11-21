from django.urls import path
from .views import UserDashboardView

app_name = "dashboard"

urlpatterns = [
    path('', UserDashboardView.as_view(), name='home'),
]