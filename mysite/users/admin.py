from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect

from users.adapters import AccountAdapter
from users.forms import CustomUserChangeForm, CustomUserCreationForm


CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_per_page = 30
    list_display = (
        "id",
        "email",
        "username",
        "date_joined",
        "last_login",
        "is_staff",
    )
    list_display_links = ("id", "email")
    list_filter = ("last_login", "date_joined", "is_staff", "is_active")
    actions = ("login", "activate", "deactivate")
    ordering = ("-id",)

    def login(
        self, r: HttpRequest, qs: QuerySet[CustomUser]
    ) -> HttpResponseRedirect:
        """Custom action to login as a user to browse the platform."""

        try:
            user = qs.get()
        except CustomUser.MultipleObjectsReturned:
            self.message_user(r, "Please select only one user")
        else:
            adapter = AccountAdapter()
            adapter.login(request=r, user=user)
            return redirect("/")

    def activate(self, request: HttpRequest, qs: QuerySet[CustomUser]) -> None:
        for user in qs:
            user.is_active = True
            user.save()
        self.message_user(request, f"{len(qs)} user(s) activated")

    def deactivate(
        self, request: HttpRequest, qs: QuerySet[CustomUser]
    ) -> None:
        for user in qs:
            user.is_active = False
            user.set_unusable_password()
            user.save()

        self.message_user(request, f"{len(qs)} user(s) deactivated")
