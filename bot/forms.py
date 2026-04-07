from django import forms
from django.core.exceptions import ValidationError
import re

from .models import Signup


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    dob = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Signup
        fields = ["role", "full_name", "contact_number", "aadhar_number", "dob", "password"]

    def clean_contact_number(self):
        cn = self.cleaned_data.get("contact_number", "")
        if not re.fullmatch(r"\d{10}", cn):
            raise ValidationError("Enter a valid 10-digit contact number.")
        return cn

    def clean_aadhar_number(self):
        a = self.cleaned_data.get("aadhar_number", "")
        if not re.fullmatch(r"\d{12}", a):
            raise ValidationError("Enter a valid 12-digit Aadhar number.")
        return a


class LoginForm(forms.Form):
    contact_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_contact_number(self):
        cn = self.cleaned_data.get("contact_number", "")
        if not re.fullmatch(r"\d{10}", cn):
            raise ValidationError("Enter a valid 10-digit contact number.")
        return cn


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ["profile_image"]
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }