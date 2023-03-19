from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, F, Count
from django.db.models.functions import Round
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import ProcessFormView

from mentorizon.forms import (
    MeetingCreateForm,
    MeetingSearchForm,
    MeetingUpdateForm,
    MentorSearchForm,
    SphereCreateForm,
    SphereFilterForm,
    SphereSearchForm,
    UserCreateForm,
    UserUpdateForm,
)
from mentorizon.models import (
    Meeting,
    MentorSession,
    RatingVote,
    Sphere,
)


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
    success_url = reverse_lazy("login")


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.prefetch_related(
        "mentor_sessions", "rating"
    ).annotate(avg_rating=Round(Avg("rating__rating_votes__rate"), 1))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        mentor_meetings = Meeting.objects.select_related(
            "mentor_session"
        ).filter(
            mentor_session__mentor_id=obj.id
        ).annotate(num_participants=Count("participants"))
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
    ).select_related("mentor_sphere").prefetch_related(
        "mentor_sessions", "rating"
    ).annotate(
        avg_rating=Round(Avg("rating__rating_votes__rate"), 1)
    ).order_by("last_name")
    template_name = "mentorizon/mentor_list.html"
    context_object_name = "mentor_list"
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        last_name = self.request.GET.get("last_name", "")
        context["search_form"] = MentorSearchForm(
            initial={"last_name": last_name}
        )
        context["filter_form"] = SphereFilterForm()
        return context

    def get_queryset(self):
        search_form = MentorSearchForm(self.request.GET)
        sphere_name = self.request.GET.get("name")
        if search_form.is_valid():
            self.queryset = self.queryset.filter(
                last_name__icontains=search_form.cleaned_data["last_name"]
            )
        if sphere_name:
            self.queryset = self.queryset.filter(
                mentor_sphere__name=sphere_name
            )
        return self.queryset


class MentorDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.filter(
        mentor_sphere__isnull=False
    ).select_related("mentor_sphere").prefetch_related(
        "mentor_sessions", "rating"
    ).annotate(avg_rating=Round(Avg("rating__rating_votes__rate"), 1))
    template_name = "mentorizon/mentor_detail.html"
    context_object_name = "mentor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
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
        "mentor_session__mentor__mentor_sphere"
    ).prefetch_related("participants").annotate(
        available_places=F("limit_of_participants") - Count("participants")
    ).order_by("date")
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.request.GET.get("topic", "")
        context["search_form"] = MeetingSearchForm(
            initial={"topic": topic}
        )
        context["filter_form"] = SphereFilterForm()
        return context

    def get_queryset(self):
        search_form = MeetingSearchForm(self.request.GET)
        sphere_name = self.request.GET.get("name")
        if search_form.is_valid():
            self.queryset = self.queryset.filter(
                topic__icontains=search_form.cleaned_data["topic"]
            )
        if sphere_name:
            self.queryset = self.queryset.filter(
                mentor_session__mentor__mentor_sphere__name=sphere_name
            )
        return self.queryset


class MeetingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Meeting
    queryset = Meeting.objects.select_related(
        "mentor_session"
    ).prefetch_related("participants").annotate(
        available_places=F("limit_of_participants") - Count("participants")
    )


class BookMeetingView(LoginRequiredMixin, ProcessFormView):

    def post(self, request, *args, **kwargs):
        meeting_id = self.kwargs["pk"]
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        participants = meeting.participants.all()
        user = self.request.user
        mentor = meeting.mentor_session.mentor
        if user is not mentor:
            if user in participants:
                meeting.participants.remove(user)
                return HttpResponseRedirect(reverse(
                    "mentorizon:meeting-detail",
                    kwargs={"pk": meeting_id}
                ))
            if len(participants) < meeting.limit_of_participants:
                meeting.participants.add(user)
                return HttpResponseRedirect(reverse(
                    "mentorizon:meeting-detail",
                    kwargs={"pk": meeting_id}
                ))

            return HttpResponseRedirect(
                reverse_lazy(
                    "mentorizon:meeting-detail",
                    kwargs={"pk": meeting_id}
                )
            )
        return HttpResponseRedirect(
            reverse_lazy(
                "mentorizon:meeting-detail",
                kwargs={"pk": meeting_id}
            )
        )


class MeetingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Meeting
    form_class = MeetingCreateForm

    def form_valid(self, form):
        if self.request.user.mentor_sphere is not None:
            meeting = Meeting.objects.create(**form.cleaned_data)
            MentorSession.objects.create(
                mentor=self.request.user,
                meeting=meeting
            )
            return HttpResponseRedirect(meeting.get_absolute_url())
        return HttpResponseRedirect(reverse("mentorizon:meeting-create"))


class MeetingUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Meeting
    form_class = MeetingUpdateForm


class MeetingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Meeting
    template_name = "mentorizon/meeting_confirm_delete.html"
    success_url = reverse_lazy("mentorizon:meeting-list")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if self.request.user.id == obj.mentor_session.mentor.id:
            return super().post(request, *args, **kwargs)
        return HttpResponseRedirect(
                reverse("mentorizon:meeting-detail", args=[obj.id])
            )


class SphereCreateView(LoginRequiredMixin, generic.CreateView):
    model = Sphere
    form_class = SphereCreateForm

    def get_success_url(self):
        pk = self.request.user.id
        return reverse_lazy("mentorizon:user-update", kwargs={"pk": pk})


class SphereListView(LoginRequiredMixin, generic.ListView):
    model = Sphere
    queryset = Sphere.objects.prefetch_related(
        "users"
    )
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = SphereSearchForm(
            initial={"name": name}
        )
        return context

    def get_queryset(self):
        search_form = SphereSearchForm(self.request.GET)
        if search_form.is_valid():
            return self.queryset.filter(
                name__icontains=search_form.cleaned_data["name"]
            )
        return self.queryset


class RateMentorView(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        mentor = get_object_or_404(get_user_model(), pk=kwargs["pk"])
        rate = self.request.POST["rate"]
        voter = self.request.user
        if voter.id != mentor.id:
            RatingVote.objects.update_or_create(
                rating_id=mentor.rating.id,
                voter_id=voter.id,
                defaults={
                    "rate": rate
                })
            return HttpResponseRedirect(
                reverse_lazy(
                    "mentorizon:mentor-detail", kwargs={"pk": mentor.id}
                )
            )

        return HttpResponseRedirect(
            reverse_lazy("mentorizon:mentor-detail", kwargs={"pk": mentor.id})
        )


def error_404_view(request, exception):
    return render(request, "404.html")


def error_500_view(request):
    return render(request, "500.html")
