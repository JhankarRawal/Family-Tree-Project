from django.db import models
from apps.accounts.models import User
from apps.families.models import Family
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramSimilarity

import os

def person_photo_path(instance, filename):
    family_id = instance.family.id if instance.family_id else "unknown"
    return os.path.join("persons", str(family_id), filename)


class Person(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='persons'
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=200, blank=True)

    death_date = models.DateField(blank=True, null=True)
    death_place = models.CharField(max_length=200, blank=True, null=True)

    is_living = models.BooleanField(default=True)

    photo = models.ImageField(
        upload_to=person_photo_path,
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_persons"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']
        indexes = [
            GinIndex(fields=["first_name", "last_name"],
                     name='person_name_gin',
            opclasses=['gin_trgm_ops','gin_trgm_ops'],), 
        ]

    def __str__(self):
        full = f"{self.first_name} {self.middle_name or ''} {self.last_name}"
        return full.strip()

    @property
    def age(self):
        """Return correct age with month/day accuracy."""
        if not self.birth_date:
            return None

        today = self.death_date or timezone.now().date()
        age = today.year - self.birth_date.year

        # Subtract 1 if birth month/day has not occurred yet this year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1

        return age
