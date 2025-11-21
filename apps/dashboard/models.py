from django.conf import settings
from django.db import models

class UserDashboardSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ Use this instead of auth.User
        on_delete=models.CASCADE
    )
    theme = models.CharField(max_length=50, default='classic')
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user}'s Dashboard Settings"
