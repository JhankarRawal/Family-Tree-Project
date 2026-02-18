from django.db import models
from django.db import models
from apps.families.models import Family
from django.conf import settings

class FamilyTreeExport(models.Model):
    EXPORT_TYPES = (
        ("pdf", "Visual PDF"),
        ("gedcom", "GEDCOM"),
        ("zip", "PDF + GEDCOM"),
    )

    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exports"
    )   
    export_type = models.CharField(max_length=10, choices=EXPORT_TYPES)
    file = models.FileField(upload_to="exports/family_trees/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.family.name} - {self.export_type}"
    

    from django.conf import settings




