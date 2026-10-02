from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Event, Profile, Registration

DT_FORMAT = "%Y-%m-%dT%H:%M"


class StyledMixin:
    """Adds the Tailwind 'field' class (defined in base.html) to every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "field"


class LoginForm(StyledMixin, AuthenticationForm):
    pass


class RegisterForm(StyledMixin, UserCreationForm):
    email = forms.EmailField()
    is_organizer = forms.BooleanField(required=False, label="I want to organize events")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.save()
        Profile.objects.create(user=user, is_organizer=self.cleaned_data["is_organizer"])
        return user


class EventForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "location", "start_time", "capacity"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = [DT_FORMAT]

    def clean_start_time(self):
        value = self.cleaned_data["start_time"]
        if not self.instance.pk and value < timezone.now():
            raise forms.ValidationError("Choose a date and time in the future.")
        return value


class RegistrationForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Registration
        fields = ["phone", "note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3})}
