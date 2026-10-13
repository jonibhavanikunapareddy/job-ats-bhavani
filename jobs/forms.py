from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Candidate, Company, JobPosting


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=160,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "name"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "autocomplete": "email"}
        )
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Candidate.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "new-password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "new-password"}
        )


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ("full_name", "email", "phone", "portfolio_url", "skills")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "portfolio_url": forms.URLInput(attrs={"class": "form-control"}),
            "skills": forms.TextInput(attrs={"class": "form-control"}),
        }


class ApplicationForm(forms.Form):
    cover_letter = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Tell the team why you are interested in this role.",
            }
        ),
    )


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "website", "location", "logo_url")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "logo_url": forms.URLInput(attrs={"class": "form-control"}),
        }


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = (
            "company",
            "title",
            "location",
            "job_type",
            "required_skills",
            "salary_range",
            "description",
            "vacancies",
            "is_active",
        )
        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "job_type": forms.Select(attrs={"class": "form-select"}),
            "required_skills": forms.TextInput(attrs={"class": "form-control"}),
            "salary_range": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "vacancies": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
