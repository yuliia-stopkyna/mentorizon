from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Sphere(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    mentor_sphere = models.ForeignKey(
        Sphere,
        on_delete=models.SET_NULL,
        null=True,
        related_name="users"
    )
    experience_description = models.TextField(null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)


class Meeting(models.Model):
    topic = models.CharField(max_length=150)
    date = models.DateTimeField()
    description = models.TextField()
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="meetings"
    )
    limit_of_participants = models.PositiveIntegerField()
    link = models.URLField()

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.topic} ({self.date})"


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
    rate = models.DecimalField(max_digits=2, decimal_places=1)

    def __str__(self) -> str:
        return f"{self.rate} from {self.voter.username}"
