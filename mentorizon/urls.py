from django.urls import path

from mentorizon.views import (
    index,
    UserCreateView,
    UserDetailView,
    UserUpdateView,
    MentorListView,
    MentorDetailView,
    MeetingListView,
    MeetingDetailView,
    book_meeting_view,
    MeetingDeleteView,
    MeetingCreateView,
    MeetingUpdateView,
    SphereCreateView,
    rate_mentor_view,
)

urlpatterns = [
    path("", index, name="index"),
    path("accounts/create/", UserCreateView.as_view(), name="user-create"),
    path("accounts/profile/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("accounts/profile/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("mentors/", MentorListView.as_view(), name="mentor-list"),
    path("meetings/", MeetingListView.as_view(), name="meeting-list"),
    path("mentor/<int:pk>/", MentorDetailView.as_view(), name="mentor-detail"),
    path("meeting/<int:pk>/", MeetingDetailView.as_view(), name="meeting-detail"),
    path("meeting/<int:pk>/book/", book_meeting_view, name="book-meeting"),
    path("meeting/create/", MeetingCreateView.as_view(), name="meeting-create"),
    path("meeting/<int:pk>/update/", MeetingUpdateView.as_view(), name="meeting-update"),
    path("meeting/<int:pk>/delete/", MeetingDeleteView.as_view(), name="meeting-delete"),
    path("sphere/create/", SphereCreateView.as_view(), name="sphere-create"),
    path("mentor/<int:pk>/rate/<int:rate>", rate_mentor_view, name="mentor-rate")
]

app_name = "mentorizon"
