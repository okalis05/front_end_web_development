from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Organization

User = get_user_model()

class LuxuryAuthForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"autocomplete": "username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    org_name = forms.CharField(label="Organization Name", max_length=180)
    org_slug = forms.SlugField(label="Organization Slug", max_length=80, help_text="Used for tenant routing (e.g. /store/?tenant=slug)")

    class Meta:
        model = User
        fields = ("username", "email", "org_name", "org_slug", "password1", "password2")

    def clean_org_slug(self):
        slug = self.cleaned_data["org_slug"]
        if Organization.objects.filter(slug=slug).exists():
            raise forms.ValidationError("That organization slug is already taken.")
        return slug
