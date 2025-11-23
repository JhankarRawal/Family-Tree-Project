# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.accounts.models import User
from apps.families.models import Family
from apps.persons.models import Person


class Relationship(models.Model):
    REL_TYPES = [
        ("parent", "Parent"),
        ("child", "Child"),
        ("spouse", "Spouse"),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="relationships")
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="relationships_from"
    )

    related_person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="relationships_to"
    )

    relationship_type = models.CharField(max_length=10, choices=REL_TYPES)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_relationships"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("person", "related_person", "relationship_type")

    def __str__(self):
        return f"{self.person} - {self.relationship_type} -> {self.related_person}"

    # -------------------------
    # VALIDATION RULES
    # -------------------------
    def clean(self):
        # Prevent self-relationship
        if self.person == self.related_person:
            raise ValidationError("A person cannot be related to themselves.")

        # Both people must be in the same family
        if self.person.family_id != self.related_person.family_id:
            raise ValidationError("Both persons must belong to the same family.")

        # Prevent circular parent-child (A parent of B but B is older)
        if self.relationship_type == "parent":
            if self.person.birth_date and self.related_person.birth_date:
                if self.person.birth_date >= self.related_person.birth_date:
                    raise ValidationError("Parent must be older than child.")

        if self.relationship_type == "child":
            if self.person.birth_date and self.related_person.birth_date:
                if self.person.birth_date <= self.related_person.birth_date:
                    raise ValidationError("Child must be younger than parent.")

    # -------------------------
    # SAVE HANDLER FOR AUTO-BIDIRECTIONAL
    # -------------------------
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Automatically create reverse relationship
        reverse_type = None
        if self.relationship_type == "parent":
            reverse_type = "child"
        elif self.relationship_type == "child":
            reverse_type = "parent"
        elif self.relationship_type == "spouse":
            reverse_type = "spouse"

        if reverse_type:
            Relationship.objects.get_or_create(
                family=self.family,
                person=self.related_person,
                related_person=self.person,
                relationship_type=reverse_type,
                defaults={"created_by": self.created_by}
            )

