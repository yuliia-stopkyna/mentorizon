from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, F, Count
from django.db.models.functions import Round
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from mentorizon.models import Meeting, Sphere, MentorSession


@login_required
def index(request):
    num_mentors = get_user_model().objects.filter(
        mentor_sphere__isnull=False
    ).count()
    now = timezone.now()
    num_meetings = Meeting.objects.filter(date__gt=now).count()
    num_spheres = Sphere.objects.count()
    context = {
        "num_mentors": num_mentors,
        "num_meetings": num_meetings,
        "num_spheres": num_spheres
    }
    return render(request, "mentorizon/index.html", context=context)


class MentorListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    queryset = get_user_model().objects.filter(
        mentor_sphere__isnull=False
    ).prefetch_related(
        "mentor_sessions", "rating"
    ).annotate(avg_rating=Round(Avg("rating__rating_votes__rate"), 1))
    template_name = "mentorizon/mentor_list.html"
    context_object_name = "mentor_list"


class MentorDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.filter(
        mentor_sphere__isnull=False
    ).prefetch_related(
        "mentor_sessions", "rating"
    ).annotate(avg_rating=Round(Avg("rating__rating_votes__rate"), 1))
    template_name = "mentorizon/mentor_detail.html"
    context_object_name = "mentor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        meetings = Meeting.objects.filter(date__gt=timezone.now()).filter(
            mentor_session__mentor_id=obj.id
        ).annotate(
            available_places=F("limit_of_participants") - Count("participants")
        )
        context["meetings"] = meetings
        return context


class MeetingListView(LoginRequiredMixin, generic.ListView):
    model = Meeting
    queryset = Meeting.objects.filter(date__gt=timezone.now()).select_related(
        "mentor_session"
    ).prefetch_related("participants").annotate(
        available_places=F("limit_of_participants") - Count("participants")
    )


class MeetingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Meeting
    queryset = Meeting.objects.filter(date__gt=timezone.now()).select_related(
        "mentor_session"
    ).prefetch_related("participants").annotate(
        available_places=F("limit_of_participants") - Count("participants")
    )


@login_required
def book_meeting_view(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    participants = meeting.participants.all()
    user = request.user
    mentor = meeting.mentor_session.mentor
    if user is not mentor:
        if user in participants:
            meeting.participants.remove(user)
            return HttpResponseRedirect(reverse(
                "mentorizon:meeting-detail",
                kwargs={"pk": pk}
            ))
        if len(participants) < meeting.limit_of_participants:
            meeting.participants.add(user)
            return HttpResponseRedirect(reverse(
                "mentorizon:meeting-detail",
                kwargs={"pk": pk}
            ))

        full_book_error = "Unfortunately, there are no available places"
        context = {
            "meeting": meeting,
            "full_book_error": full_book_error
        }
        return render(request, "mentorizon/meeting_detail.html", context=context)


class MeetingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Meeting
    template_name = "mentorizon/meeting_confirm_delete.html"
    success_url = reverse_lazy("mentorizon:meeting-list")
