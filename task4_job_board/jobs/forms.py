from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Application, Candidate, Employer, Job, Resume

FILE_CLASSES = (
    "block w-full text-sm text-slate-600 file:mr-4 file:rounded-xl file:border-0 "
    "file:bg-indigo-100 file:px-4 file:py-2 file:font-medium file:text-indigo-700 hover:file:bg-indigo-200"
)


class StyledMixin:
    """Adds Tailwind classes to every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs["class"] = FILE_CLASSES
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "field"


class LoginForm(StyledMixin, AuthenticationForm):
    pass


class RegisterForm(StyledMixin, UserCreationForm):
    ROLES = [("candidate", "I am looking for a job"), ("employer", "I am hiring")]
    role = forms.ChoiceField(choices=ROLES, label="I want to")
    name = forms.CharField(max_length=150, label="Full name (or company name if hiring)")
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.save()
        if self.cleaned_data["role"] == "employer":
            Employer.objects.create(user=user, company_name=self.cleaned_data["name"])
        else:
            Candidate.objects.create(user=user, full_name=self.cleaned_data["name"])
        return user


class JobForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "location", "job_type", "salary", "is_open"]
        labels = {"is_open": "Accepting applications"}
        widgets = {"description": forms.Textarea(attrs={"rows": 8})}


class ResumeForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["title", "file"]


class ApplicationForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Application
        fields = ["resume", "cover_letter"]
        widgets = {"cover_letter": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, candidate, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resume"].queryset = candidate.resumes.all()
        self.fields["resume"].required = True
        self.fields["resume"].empty_label = "Choose a resume"
