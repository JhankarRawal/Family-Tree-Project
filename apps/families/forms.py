from django import forms
from .models import Family, JoinRequest , Invitation


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name', 'description']


class JoinByCodeForm(forms.Form):
    code = forms.CharField(
        max_length=12,
        required=True,
        label="Family Code",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Family Code'})
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional message'}),
        label="Message"
    )

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['recipient_email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }


