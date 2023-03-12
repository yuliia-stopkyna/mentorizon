from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

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


class MentorSearchForm(forms.Form):
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by last name..."})
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
        help_text="Enter in format: YYYY-MM-DD HH:MM",
        validators=[MinValueValidator(
            limit_value=timezone.now() + timezone.timedelta(minutes=30),
            message="Meeting date and time should be in future"
        )]
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


class MeetingUpdateForm(MeetingCreateForm):

    def clean_limit_of_participants(self):
        data = self.cleaned_data["limit_of_participants"]
        current_participants = self.instance.participants.count()
        if data < current_participants:
            raise ValidationError("Limit of participants can't be less than "
                                  "current number of participants: "
                                  f"{current_participants}")
        return data


class MeetingSearchForm(forms.Form):
    topic = forms.CharField(
        max_length=150,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by topic..."})
    )


class SphereCreateForm(forms.ModelForm):

    class Meta:
        model = Sphere
        fields = "__all__"


class SphereSearchForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name..."})
    )


class SphereFilterForm(forms.ModelForm):
    name = forms.ModelChoiceField(
        queryset=Sphere.objects.all(),
        empty_label="Sphere",
        to_field_name="name",
        required=False,
        label="",
        widget=forms.Select()
    )

    class Meta:
        model = Sphere
        fields = ("name",)
