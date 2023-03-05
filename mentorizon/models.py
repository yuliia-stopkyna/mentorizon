from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone


class Sphere(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="name_unique",
                violation_error_message="Sphere with this name already exists.")
        ]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    mentor_sphere = models.ForeignKey(
        Sphere,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users"
    )
    experience_description = models.TextField(null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    def get_absolute_url(self):
        return reverse("mentorizon:user-detail", kwargs={"pk": self.pk})


class MeetingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(date__gt=timezone.now())


class Meeting(models.Model):
    topic = models.CharField(max_length=150)
    date = models.DateTimeField()
    description = models.TextField()
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="meetings"
    )
    limit_of_participants = models.PositiveIntegerField()
    link = models.URLField()
    objects = MeetingManager()

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.topic} ({self.date})"


class MentorSessionModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            meeting__date__gt=timezone.now()
        )


class MentorSession(models.Model):
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor_sessions"
    )
    meeting = models.OneToOneField(
        Meeting,
        on_delete=models.CASCADE,
        related_name="mentor_session"
    )
    objects = MentorSessionModel()

    def __str__(self) -> str:
        return (
            "Session with "
            f"{self.mentor.first_name} {self.mentor.last_name}"
        )


class Rating(models.Model):
    mentor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="rating",
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"Rating of {self.mentor.username}"


class RatingVote(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name="rating_votes")
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rating_votes"
    )
    rate = models.IntegerField(
        validators=[
            MinValueValidator(limit_value=0),
            MaxValueValidator(limit_value=5)
        ]
    )

    def __str__(self) -> str:
        return f"{self.rate} from {self.voter.username}"
