from django.db import models
from django.contrib.auth.models import User
from apps.families.models import Family
from config import settings
User = settings.AUTH_USER_MODEL
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    TARGET_CHOICES = [
        ("person", "Person"),
        ("relationship", "Relationship"),
        ("member", "Member"),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_id = models.IntegerField()

    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} {self.action_type} {self.target_type} ({self.target_id})"


