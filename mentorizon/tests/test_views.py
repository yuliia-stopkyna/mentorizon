from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from mentorizon.models import Sphere, Meeting, MentorSession


class PrivateTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        users = (
            ("test", "Ivan", "Ivanenko"),
            ("test_1", "Vasyl", "Vasylenko")
        )
        for username, first_name, last_name in users:
            get_user_model().objects.create_user(
                username=username,
                password="test12345",
                first_name=first_name,
                last_name=last_name
            )
        Sphere.objects.create(
            name="Art"
        )
        Sphere.objects.create(
            name="Languages"
        )
        Meeting.objects.create(
            topic="Test meeting1",
            date=timezone.now() + timezone.timedelta(days=30),
            description="This is a test",
            limit_of_participants=2,
            link="google.com"
        )
        Meeting.objects.create(
            topic="Test meeting2",
            date=timezone.now() + timezone.timedelta(days=30),
            description="This is a test",
            limit_of_participants=1,
            link="google.com"
        )

    def setUp(self) -> None:
        self.sphere1 = Sphere.objects.get(pk=1)
        self.sphere2 = Sphere.objects.get(pk=2)
        self.mentor = get_user_model().objects.get(pk=1)
        self.user = get_user_model().objects.get(pk=2)
        self.mentor.mentor_sphere = self.sphere1
        self.mentor.save()
        self.user.mentor_sphere = self.sphere2
        self.user.save()
        self.meeting1 = Meeting.objects.get(pk=1)
        self.meeting2 = Meeting.objects.get(pk=2)
        self.mentor_session1 = MentorSession.objects.create(
            mentor=self.mentor,
            meeting=self.meeting1
        )
        self.mentor_session2 = MentorSession.objects.create(
            mentor=self.user,
            meeting=self.meeting2
        )
        self.meeting1.participants.add(self.user)
        self.meeting2.participants.add(self.mentor)
        self.client.force_login(self.user)

    def test_user_detail_meetings_info(self):
        response = self.client.get(
            reverse("mentorizon:user-detail", kwargs={"pk": self.user.id})
        )

        self.assertEquals(response.context_data["mentor_meetings"].count(), 1)
        self.assertEquals(
            response.context_data["particip_meetings"].count(),
            1
        )

    def test_user_rating_vote(self):
        self.client.get(reverse("mentorizon:mentor-rate", kwargs={
            "pk": self.mentor.id,
            "rate": 5
        }))
        response1 = self.client.get(
            reverse("mentorizon:mentor-detail", kwargs={"pk": self.mentor.id})
        )
        self.client.get(reverse("mentorizon:mentor-rate", kwargs={
            "pk": self.user.id,
            "rate": 5
        }))
        response2 = self.client.get(
            reverse("mentorizon:mentor-detail", kwargs={"pk": self.user.id})
        )
        self.client.get(reverse("mentorizon:mentor-rate", kwargs={
            "pk": self.mentor.id,
            "rate": 4
        }))
        response3 = self.client.get(
            reverse("mentorizon:mentor-detail", kwargs={"pk": self.mentor.id})
        )

        self.assertContains(response1, "Rating: 5.0")
        self.assertContains(response2, "Rating: 0")
        self.assertContains(response3, "Rating: 4.0")

    def test_book_meeting(self):
        response1 = self.client.get(
            reverse("mentorizon:meeting-detail", kwargs={
                "pk": self.meeting1.id
            })
        )
        self.client.get(reverse("mentorizon:book-meeting", kwargs={
            "pk": self.meeting1.id
        }))
        response2 = self.client.get(
            reverse("mentorizon:meeting-detail", kwargs={
                "pk": self.meeting1.id
            })
        )

        self.assertContains(response1, "Unbook")
        self.assertContains(response2, "Book")

    def test_mentors_sphere_filter(self):
        form_data1 = {
            "name": "Art"
        }
        response1 = self.client.get(
            reverse("mentorizon:mentor-list"), data=form_data1
        )
        form_data2 = {
            "name": "Languages"
        }
        response2 = self.client.get(
            reverse("mentorizon:mentor-list"), data=form_data2
        )

        self.assertContains(
            response1,
            self.mentor.last_name
        )
        self.assertNotContains(
            response1,
            self.user.last_name
        )
        self.assertContains(
            response2,
            self.user.last_name
        )
        self.assertNotContains(
            response2,
            self.mentor.last_name
        )

    def test_meetings_sphere_filter(self):
        form_data1 = {
            "name": "Art"
        }
        response1 = self.client.get(
            reverse("mentorizon:meeting-list"), data=form_data1
        )
        form_data2 = {
            "name": "Languages"
        }
        response2 = self.client.get(
            reverse("mentorizon:meeting-list"), data=form_data2
        )

        self.assertContains(
            response1,
            self.meeting1.topic
        )
        self.assertNotContains(
            response1,
            self.meeting2.topic
        )
        self.assertContains(
            response2,
            self.meeting2.topic
        )
        self.assertNotContains(
            response2,
            self.meeting1.topic
        )

    def test_search_mentors(self):
        form_data = {
            "last_name": "ivanenko"
        }
        response = self.client.get(
            reverse("mentorizon:mentor-list"), data=form_data
        )

        self.assertContains(response, self.mentor.last_name)
        self.assertNotContains(response, self.user.last_name)

    def test_search_meetings(self):
        form_data = {
            "topic": "meeting1"
        }
        response = self.client.get(
            reverse("mentorizon:meeting-list"), data=form_data
        )

        self.assertContains(response, self.meeting1.topic)
        self.assertNotContains(response, self.meeting2.topic)

    def test_search_spheres(self):
        form_data = {
            "name": "lang"
        }
        response = self.client.get(
            reverse("mentorizon:sphere-list"), data=form_data
        )

        self.assertContains(response, self.sphere2.name)
        self.assertNotContains(response, self.sphere1.name)

    def test_meeting_update(self):
        form_data1 = {
            "limit_of_participants": 0
        }
        response1 = self.client.post(
            reverse(
                "mentorizon:meeting-update",
                args=[self.meeting2.id]
            ),
            data=form_data1
        )
        form_data2 = {
            "date": timezone.now() - timezone.timedelta(days=1)
        }
        response2 = self.client.post(
            reverse(
                "mentorizon:meeting-update",
                args=[self.meeting2.id]
            ), data=form_data2
        )

        self.assertContains(
            response1, "less than current number of participants:"
        )
        self.assertContains(
            response2, "Meeting date and time should be in future"
        )

    def test_meeting_create_with_mentor_sphere(self):
        form_data = {
            "topic": "Test meeting3",
            "date": timezone.now() + timezone.timedelta(days=5),
            "description": "This is another test meeting",
            "limit_of_participants": 2,
            "link": "google.com"
        }
        self.client.post(reverse("mentorizon:meeting-create"), data=form_data)
        response = self.client.get(reverse("mentorizon:meeting-list"))

        self.assertContains(response, "Test meeting3")
        self.assertTrue(
            MentorSession.objects.filter(meeting__topic="Test meeting3")
        )
        self.assertEqual(Meeting.objects.get(pk=3).mentor_session.mentor.id, 2)

    def test_meeting_create_without_mentor_sphere(self):
        form_data = {
            "topic": "Test meeting4",
            "date": timezone.now() + timezone.timedelta(days=5),
            "description": "This is another test meeting",
            "limit_of_participants": 2,
            "link": "google.com"
        }
        self.user.mentor_sphere = None
        self.user.save()
        self.client.post(reverse("mentorizon:meeting-create"), data=form_data)
        response = self.client.get(reverse("mentorizon:meeting-list"))

        self.assertNotContains(response, "Test meeting4")
        self.assertFalse(
            MentorSession.objects.filter(meeting__topic="Test meeting4")
        )
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(pk=4)

    def test_meeting_delete(self):
        self.client.post(reverse(
            "mentorizon:meeting-delete", args=[self.meeting2.id]
        ))
        self.client.post(reverse(
            "mentorizon:meeting-delete", args=[self.meeting1.id]
        ))

        self.assertTrue(Meeting.objects.filter(pk=self.meeting1.id))
        with self.assertRaises(ObjectDoesNotExist):
            Meeting.objects.get(pk=self.meeting2.id)
