import secrets

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models

# local imports
from django_sso.core.db.models import BaseModel

# django imports
from django_sso.users.managers import UserManager

# utils
from django_sso.utils.string import normalize_uri


class User(BaseModel, AbstractUser):
    """
    User model
    """

    username = models.CharField("Username", max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField("Email address", unique=True)
    profile_picture = models.ImageField(
        "Profile picture",
        upload_to="users/profile_pictures/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f"{self.username}"


class Application(BaseModel):
    """
    Applications that will use this services as their Identify Provider.
    """

    name = models.CharField("Name", max_length=256)

    client_id = models.CharField(max_length=152, unique=True, editable=False)
    client_secret = models.CharField(max_length=256, unique=True, editable=False)

    redirect_uris = models.TextField(help_text="Newline-separated list of allowed redirect URIs.")
    allowed_scopes = models.TextField(default="openid email profile")

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = self._generate_unique_client_id()

        if not self.client_secret:
            raw_secret = secrets.token_urlsafe(64)
            self._raw_client_secret = raw_secret
            self.client_secret = make_password(raw_secret, hasher="argon2")

        return super().save(*args, **kwargs)

    def _generate_unique_client_id(self, length=32):
        token = secrets.token_urlsafe(length)

        while Application.objects.filter(client_id=token).exists():
            token = secrets.token_urlsafe(length)

        return token

    def get_redirect_uris(self):
        return [normalize_uri(uri.strip()) for uri in self.redirect_uris.splitlines() if uri.strip()]

    def get_allowed_scopes(self):
        return [s.strip() for s in self.allowed_scopes.split() if s.strip()]

    def __str__(self):
        return self.name
