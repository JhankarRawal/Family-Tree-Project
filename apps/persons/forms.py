from django import forms
from .models import Person

class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "birth_date",
            "birth_place",
            "death_date",
            "death_place",
            "is_living",
            "photo",
            "notes",
        ]
        widgets = {
            "birth_date": forms.DateInput(
                attrs={
                    "type": "date",   # HTML5 calendar
                    "class": "form-control"
                }
            ),
            "death_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),
            "notes": forms.Textarea(attrs={"rows": 4, "class": "form-control"})

        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            if not photo.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                raise forms.ValidationError("Only JPG, PNG, and WEBP images are allowed.")
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image size must be under 5MB.")
        return photo
