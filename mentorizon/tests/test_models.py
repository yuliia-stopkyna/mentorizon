from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from mentorizon.models import Sphere, Meeting, MentorSession, Rating


class SphereModelTest(TestCase):

    def test_capitalize_name(self):
        sphere = Sphere.objects.create(
            name="psyCHOloGy"
        )

        self.assertEqual(sphere.name, "Psychology")


class MeetingModelTest(TestCase):

    def test_custom_meeting_manager(self):
        Meeting.objects.create(
            topic="Test",
            date=timezone.now() - timezone.timedelta(days=1),
            description="Test meeting",
            limit_of_participants=2,
            link="google.com"
        )
        Meeting.objects.create(
            topic="Test",
            date=timezone.now() + timezone.timedelta(days=1),
            description="Test meeting",
            limit_of_participants=2,
            link="google.com"
        )

        self.assertEqual(Meeting.objects.count(), 1)


class MentorSessionModelTest(TestCase):

    def test_custom_mentor_session_manager(self):
        mentor = get_user_model().objects.create_user(
            username="Test",
            password="test12345",
            first_name="Ivan",
            last_name="Ivanenko"
        )
        meeting1 = Meeting.objects.create(
            topic="Test",
            date=timezone.now() - timezone.timedelta(days=1),
            description="Test meeting",
            limit_of_participants=2,
            link="google.com"
        )
        meeting2 = Meeting.objects.create(
            topic="Test",
            date=timezone.now() + timezone.timedelta(days=1),
            description="Test meeting",
            limit_of_participants=2,
            link="google.com"
        )
        MentorSession.objects.create(
            mentor=mentor,
            meeting=meeting1
        )
        MentorSession.objects.create(
            mentor=mentor,
            meeting=meeting2
        )

        self.assertEqual(MentorSession.objects.count(), 1)


class UserModelTest(TestCase):

    def test_rating_create(self):
        get_user_model().objects.create_user(
            username="test",
            password="test12345",
            first_name="Ivan",
            last_name="Ivanenko"
        )

        self.assertTrue(Rating.objects.count(), 1)
