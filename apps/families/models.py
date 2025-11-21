from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from .utils import generate_family_code


User = settings.AUTH_USER_MODEL


class Family(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=12, unique=True, db_index=True)
    owner = models.ForeignKey(User, related_name='owned_families', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_family_code()
        super().save(*args, **kwargs)


class FamilyMembership(models.Model):
    ROLE_CHOICES = (
    ('owner', 'Owner'),
    ('admin', 'Admin'),
    ('member', 'Member'),
    )
    family = models.ForeignKey(Family, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='family_memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(default=timezone.now)


class Meta:
    unique_together = ('family', 'user')


def __str__(self):
    return f"{self.user} in {self.family} as {self.role}"
class Invitation(models.Model):
    """
    Represents an invitation sent by a family admin/owner to a user to join a family.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        'Family', 
        on_delete=models.CASCADE, 
        related_name='invitations'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_invitations'
    )
    recipient_email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    message = models.TextField(blank=True, null=True)
    accepted = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'

    def __str__(self):
        return f"Invitation to {self.recipient_email} for {self.family.name}"


class JoinRequest(models.Model):

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"  # used if member is removed

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (CANCELLED, "Cancelled"),
    ]
    family = models.ForeignKey(Family, related_name='join_requests', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='join_requests', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default=PENDING)    
    processed_by = models.ForeignKey(User, related_name='processed_join_requests', null=True, blank=True, on_delete=models.SET_NULL)
    processed_at = models.DateTimeField(null=True, blank=True)
class Meta:
    unique_together = ('family', 'user')
    ordering = ['-created_at']
def __str__(self):
        return f"JoinRequest: {self.user.get_username()} -> {self.family.name} ({self.status})"




