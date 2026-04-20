from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm

from .models import AcademicClass, CustomUser


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    academic_class = forms.ModelChoiceField(
        queryset=AcademicClass.objects.all(),
        required=False,
        empty_label="Select Class (for student)",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    parent_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Parent email (for student)"}),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        if not cleaned_data.get("email"):
            raise forms.ValidationError("Email is required for OTP verification.")
        if cleaned_data.get("role") == CustomUser.Role.STUDENT and not cleaned_data.get("academic_class"):
            raise forms.ValidationError("Class is required when registering as student.")
        if cleaned_data.get("role") == CustomUser.Role.STUDENT and not cleaned_data.get("parent_email"):
            raise forms.ValidationError("Parent email is required when registering as student.")
        return cleaned_data


class LoginWithPasswordForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise forms.ValidationError("Account inactive. Complete OTP verification.")
        cleaned_data["user"] = user
        return cleaned_data


class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={"class": "form-control"}))
