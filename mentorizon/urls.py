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
    meeting_create_view,
    SphereCreateView,
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
    path("meeting/create/", meeting_create_view, name="meeting-create"),
    path("meeting/<int:pk>/delete/", MeetingDeleteView.as_view(), name="meeting-delete"),
    path("sphere/create/", SphereCreateView.as_view(), name="sphere-create")
]

app_name = "mentorizon"
