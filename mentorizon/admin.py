from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from mentorizon.models import (
    Meeting,
    MentorSession,
    Rating,
    RatingVote,
    Sphere,
    User,
)


@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Personal info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "email",
                    )
                },
            ),
            (
                "Mentor info",
                {
                    "fields": (
                        "mentor_sphere",
                        "experience_description",
                        "years_of_experience"
                    )
                }
            )
        )
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            (
                "Mentor info",
                {
                    "fields": (
                        "mentor_sphere",
                        "experience_description",
                        "years_of_experience"
                    )
                }
            ),
        )
    )
    list_display = UserAdmin.list_display + (
        "mentor_sphere",
        "experience_description",
        "years_of_experience"
    )


@admin.register(Sphere)
class SphereAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("topic", "date", "limit_of_participants", "link")
    search_fields = ("topic", "date")


@admin.register(MentorSession)
class MentorSessionAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ("mentor", "meeting")
    search_fields = ("mentor__username",)


admin.site.register(Rating)


@admin.register(RatingVote)
class RatingVoteAdmin(admin.ModelAdmin):
    list_display = ("rating", "voter", "rate")
