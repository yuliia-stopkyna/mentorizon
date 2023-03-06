from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from mentorizon.models import Meeting, Sphere


class UserCreateForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )


class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
            "mentor_sphere",
            "years_of_experience",
            "experience_description"
        )


class MeetingCreateForm(forms.ModelForm):
    date = forms.DateTimeField(
        label="Date and time",
        required=True,
        input_formats=settings.DATETIME_INPUT_FORMATS + [
            "%d/%m/%y %H:%M",
            "%d.%m.%y %H:%M",
            "%d/%m/%Y %H:%M",
            "%d.%m.%Y %H:%M",
        ],
        help_text="Enter in format: YYYY-MM-DD HH:MM"
    )

    class Meta:
        model = Meeting
        fields = (
            "topic",
            "date",
            "description",
            "limit_of_participants",
            "link"
        )


class SphereCreateForm(forms.ModelForm):

    class Meta:
        model = Sphere
        fields = "__all__"
