from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

ALLOWED_EMAILS = [
    "friend1@gmail.com",
    "chanelmizani@gmail.com",
    "marcowolff619@gmail.com",
]

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email not in ALLOWED_EMAILS:
            raise forms.ValidationError("ask Chanel for info/password")

        return email

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]