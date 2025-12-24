from __future__ import annotations
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Organization

User = get_user_model()

class LuxeLoginForm(AuthenticationForm):
    username = forms.CharField(label="Email or Username")

class LuxeSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class OrgCreateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ("name", "slug", "legal_name", "country", "risk_tier")
        widgets = {
            "risk_tier": forms.Select(choices=[("standard", "Standard"), ("high", "High")])
        }
