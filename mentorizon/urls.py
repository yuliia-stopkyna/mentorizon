from django.urls import path

from mentorizon.views import (
    index,
    MentorListView,
    MentorDetailView,
    MeetingListView,
    MeetingDetailView,
    book_meeting_view,
    MeetingDeleteView
)

urlpatterns = [
    path("", index, name="index"),
    path("mentors/", MentorListView.as_view(), name="mentor-list"),
    path("meetings/", MeetingListView.as_view(), name="meeting-list"),
    path("mentor/<int:pk>/", MentorDetailView.as_view(), name="mentor-detail"),
    path("meeting/<int:pk>/", MeetingDetailView.as_view(), name="meeting-detail"),
    path("meeting/<int:pk>/book/", book_meeting_view, name="book-meeting"),
    path("meeting/<int:pk>/delete/", MeetingDeleteView.as_view(), name="meeting-delete")
]

app_name = "mentorizon"
