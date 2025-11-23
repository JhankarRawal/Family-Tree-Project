from django import forms
from apps.persons.models import Person
from .models import Relationship

class RelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = ["related_person", "relationship_type"]

    def __init__(self, *args, **kwargs):
        family = kwargs.pop("family", None)
        person = kwargs.pop("person", None)
        super().__init__(*args, **kwargs)

        # Only list members of same family EXCEPT the person itself
        if family:
            self.fields["related_person"].queryset = family.persons.exclude(id=person.id)

        self.fields["relationship_type"].widget = forms.HiddenInput()
