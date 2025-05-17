from django.contrib import admin, messages
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from django_sso.users.forms import UserAdminChangeForm, UserAdminCreationForm

# local
from .models import Application

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["email", "username", "is_superuser"]
    search_fields = ["first_name", "last_name", "email"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "client_id", "client_secret", "created_at", "updated_at")
    list_display = ("name", "client_id", "is_active", "created_at")
    search_fields = ("name", "client_id")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("name", "is_active")}),
        (_("OAuth2 Credentials"), {"fields": ("client_id", "client_secret")}),
        (_("Security Settings"), {"fields": ("redirect_uris", "allowed_scopes")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        raw_secret = getattr(obj, "_raw_client_secret", None)
        if raw_secret:
            messages.add_message(
                request,
                messages.WARNING,
                f"Raw Client Secret (save this now, it won't be shown again): {raw_secret}",
            )
