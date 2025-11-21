from django import forms
from .models import Person

class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = [
            "first_name", "last_name", "gender",
            "birth_date", "death_date", "birth_place",
            "photo", "notes", "is_living"
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
            )
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Max file size is 5MB.")
            if not photo.content_type in ["image/jpeg", "image/png"]:
                raise forms.ValidationError("Photo must be JPG or PNG.")
        return photo
