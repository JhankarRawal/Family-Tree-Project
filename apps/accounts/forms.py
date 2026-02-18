from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")


# accounts/forms.py


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_photo', 'bio', 'phone_number', 'is_public']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

