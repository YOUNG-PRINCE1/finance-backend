from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=50,
        help_text="Choose a unique username (letters, numbers, @/./+/-/_ only).",
        error_messages={
            'invalid': "Please use only letters, numbers, and @/./+/-/_ characters.",
            'required': "Username is required.",
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
