from django.db import models
from apps.families.models import Family
from django.utils import timezone
import os

def person_photo_path(instance, filename):
    # Use instance.pk safely (may be None during create) — store under temporary name if needed
    family_id = instance.family.id if instance.family_id else "unknown"
    return os.path.join("persons", str(family_id), filename)

class Person(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='persons')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=200, blank=True)
    is_living = models.BooleanField(default=True)
    photo = models.ImageField(upload_to=person_photo_path, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.now().date()
        end = self.death_date or today
        return end.year - self.birth_date.year
