from django import forms
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from allauth.core import context
from allauth.socialaccount.forms import SignupForm as SocialSignupForm

from django.contrib.auth import get_user_model
from .models import JobAlertPreference, Profile, SignupRecord


class ResumeBuilderForm(forms.Form):
    full_name = forms.CharField(max_length=100, label="Full name")
    headline = forms.CharField(
        max_length=160,
        required=False,
        label="Professional headline",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Product Designer"}),
    )
    email = forms.EmailField(max_length=254, label="Email")
    phone = forms.CharField(max_length=30, required=False, label="Phone")
    location = forms.CharField(max_length=100, required=False, label="Location")
    summary = forms.CharField(
        max_length=1500,
        required=False,
        label="Professional summary",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    skills = forms.CharField(
        max_length=500,
        required=False,
        label="Skills",
        help_text="Separate skills with commas.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    experience = forms.CharField(
        max_length=3000,
        required=False,
        label="Experience",
        help_text="Add one role or achievement per line.",
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    education = forms.CharField(
        max_length=2000,
        required=False,
        label="Education",
        help_text="Add one qualification per line.",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    links = forms.CharField(
        max_length=500,
        required=False,
        label="Portfolio or professional links",
        help_text="Add one URL per line.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class JobAlertPreferenceForm(forms.ModelForm):
    class Meta:
        model = JobAlertPreference
        fields = ("title", "location", "skills", "job_type", "work_mode", "experience")
        widgets = {
            "title": forms.TextInput(attrs={"maxlength": 100}),
            "location": forms.TextInput(attrs={"maxlength": 100}),
            "skills": forms.TextInput(attrs={"maxlength": 200}),
            "job_type": forms.Select(),
            "work_mode": forms.Select(),
            "experience": forms.TextInput(attrs={"maxlength": 100}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not any(cleaned_data.get(field) for field in self.Meta.fields):
            raise forms.ValidationError("Add at least one job alert criterion.")
        return cleaned_data


class TalentBridgeSocialSignupForm(SocialSignupForm):
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label="Account type",
        widget=forms.Select(attrs={"autocomplete": "off"}),
    )
    password1 = forms.CharField(
        label="Create a password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    company_name = forms.CharField(
        label="Company name",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "organization",
                "placeholder": "Enter your company name",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(["email", "username", "password1", "password2", "role", "company_name"])
        request = context.request
        self.requested_role = request.session.get("talentbridge.social_signup_role")
        if self.requested_role in dict(Profile.ROLE_CHOICES):
            self.fields["role"].initial = self.requested_role
            self.fields["role"].widget = forms.HiddenInput()

    def clean_email(self):
        email = super().clean_email().strip().lower()
        User = get_user_model()
        if email and User.objects.filter(email__iexact=email).exists():
            # Existing verified Google identities are connected by allauth before
            # this signup form is reached; never create a second user here.
            raise forms.ValidationError("An account with this email already exists. Please sign in instead.")
        if email and SignupRecord.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email has already been registered. Please sign in.")
        return email

    def clean_role(self):
        if self.requested_role in dict(Profile.ROLE_CHOICES):
            return self.requested_role
        return self.cleaned_data["role"]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "The passwords do not match.")
        if password1:
            try:
                validate_password(password1)
            except forms.ValidationError as exc:
                self.add_error("password1", exc)
        if (
            cleaned_data.get("role") == "employer"
            and not cleaned_data.get("company_name", "").strip()
        ):
            self.add_error("company_name", "Enter your company name to continue.")
        return cleaned_data

    def save(self, request):
        with transaction.atomic():
            return super().save(request)
