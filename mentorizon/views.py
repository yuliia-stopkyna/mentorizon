from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Avg, F, Count
from django.db.models.functions import Round
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic
from django.shortcuts import render, get_object_or_404

from mentorizon.forms import (
    UserCreateForm,
    UserUpdateForm,
    MeetingCreateForm,
    SphereCreateForm
)
from mentorizon.models import Meeting, Sphere, MentorSession, Rating, RatingVote


@login_required
def index(request):
    num_mentors = get_user_model().objects.filter(
        mentor_sphere__isnull=False
    ).count()
    num_meetings = Meeting.objects.count()
    num_spheres = Sphere.objects.count()
    context = {
        "num_mentors": num_mentors,
        "num_meetings": num_meetings,
        "num_spheres": num_spheres
    }
    return render(request, "mentorizon/index.html", context=context)


class UserCreateView(generic.CreateView):
    model = get_user_model()
    form_class = UserCreateForm

    def get_success_url(self):
        Rating.objects.create(mentor=self.object)
        return reverse_lazy("login")


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.prefetch_related(
        "mentor_sessions", "rating"
    ).annotate(avg_rating=Round(Avg("rating__rating_votes__rate"), 1))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = super().get_object()
        mentor_meetings = Meeting.objects.select_related("mentor_session").filter(
            mentor_session__mentor_id=obj.id
        )
        particip_meetings = Meeting.objects.prefetch_related(
            "participants"
        ).filter(participants__id=obj.id)
        context["mentor_meetings"] = mentor_meetings
        context["particip_meetings"] = particip_meetings
        return context


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = "mentorizon/user_update.html"


class MentorListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    queryset = get_user_model().objects.filter(
        mentor_sphere__isnull=False
    ).prefetch_related(
        "mentor_sessions", "rating"
    ).annotate(avg_rating=Round(Avg("rating__rating_votes__rate"), 1))
    template_name = "mentorizon/mentor_list.html"
    context_object_name = "mentor_list"
    paginate_by = 6


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
        meetings = Meeting.objects.select_related("mentor_session").filter(
            mentor_session__mentor_id=obj.id
        ).annotate(
            available_places=F("limit_of_participants") - Count("participants")
        )
        context["meetings"] = meetings
        return context


class MeetingListView(LoginRequiredMixin, generic.ListView):
    model = Meeting
    queryset = Meeting.objects.select_related(
        "mentor_session"
    ).prefetch_related("participants").annotate(
        available_places=F("limit_of_participants") - Count("participants")
    )
    paginate_by = 6


class MeetingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Meeting
    queryset = Meeting.objects.select_related(
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


class MeetingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Meeting
    form_class = MeetingCreateForm

    def form_valid(self, form):
        if form.cleaned_data["date"] <= timezone.now():
            form.add_error(
                "date",
                ValidationError(
                    message="Meeting date and time should be in future"
                ))
            return super().form_invalid(form)
        meeting = Meeting.objects.create(**form.cleaned_data)
        MentorSession.objects.create(
            mentor=self.request.user,
            meeting=meeting
        )
        return HttpResponseRedirect(meeting.get_absolute_url())


class MeetingUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Meeting
    form_class = MeetingCreateForm

    def form_valid(self, form):
        if form.cleaned_data["date"] <= timezone.now():
            form.add_error(
                "date",
                ValidationError(
                    message="Meeting date and time should be in future"
                ))
            return super().form_invalid(form)

        if (
            form.cleaned_data["limit_of_participants"] < self.object.participants.count()
        ):
            form.add_error(
                "limit_of_participants",
                ValidationError(
                    message="Limit of participants can't be less than "
                            "current number of participants: "
                            f"{self.object.participants.count()}"
                ))
            return super().form_invalid(form)

        return super().form_valid(form)


class MeetingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Meeting
    template_name = "mentorizon/meeting_confirm_delete.html"
    success_url = reverse_lazy("mentorizon:meeting-list")


class SphereCreateView(LoginRequiredMixin, generic.CreateView):
    model = Sphere
    form_class = SphereCreateForm

    def get_success_url(self):
        pk = self.request.user.id
        return reverse_lazy("mentorizon:user-update", kwargs={"pk": pk})


@login_required
def rate_mentor_view(request, pk, rate):
    mentor = get_object_or_404(get_user_model(), pk=pk)
    user = request.user
    mentor_votes = RatingVote.objects.filter(
        rating_id=mentor.rating.id
    )
    if user.id != mentor.id:
        if mentor_votes.filter(voter_id=user.id):
            mentor_votes.filter(voter_id=user.id).update(rate=rate)
        else:
            RatingVote.objects.create(
                rating_id=mentor.rating.id,
                voter=user,
                rate=rate
            )
        return HttpResponseRedirect(
            reverse_lazy("mentorizon:mentor-detail", args=[pk])
        )
    return HttpResponseRedirect(
            reverse_lazy("mentorizon:mentor-detail", args=[pk])
        )
