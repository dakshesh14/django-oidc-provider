import json
import secrets
from urllib.parse import urlencode

import jwt

# django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DJLoginView
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.timezone import now
from django.views import View
from django.views.generic.edit import FormView

# rest framework
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django_sso.utils.string import normalize_uri

from .forms import RegisterForm
from .models import Application

# local
from .serializers import TokenRequestSerializer

# utils
from .utils.auth import create_and_cache_auth_code

User = get_user_model()


class AuthorizeView(LoginRequiredMixin, View):
    login_url = "/api/users/login/"

    def get(self, request, *args, **kwargs):
        client_id = request.GET.get("client_id")
        redirect_uri = request.GET.get("redirect_uri")
        state = request.GET.get("state", "")
        scope = request.GET.get("scope", "openid")
        requested_scopes = scope.split()

        client = Application.objects.filter(client_id=client_id, is_active=True).first()
        if not client:
            return redirect("/error?error=invalid_client")

        allowed_scopes = set(client.get_allowed_scopes())
        granted_scopes = [s for s in requested_scopes if s in allowed_scopes]

        if normalize_uri(redirect_uri) not in client.get_redirect_uris():
            return redirect("/error?error=invalid_redirect_uri")

        if not granted_scopes:
            return redirect("/error?error=invalid_scope")

        auth_code = create_and_cache_auth_code(request.user, client, redirect_uri, granted_scopes)

        query = urlencode({"code": auth_code, "state": state})
        return redirect(f"{redirect_uri}?{query}")


class TokenView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request, *args, **kwargs):
        serializer = TokenRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({"error": "invalid_request", "error_description": serializer.errors}, status=400)

        data = serializer.validated_data
        client_id = data["client_id"]
        client_secret = data["client_secret"]
        code = data["code"]
        redirect_uri = data["redirect_uri"]
        grant_type = data["grant_type"]  # noqa

        client = Application.objects.filter(client_id=client_id).first()
        if not client or not check_password(client_secret, client.client_secret):
            return Response({"error": "invalid_client"}, status=status.HTTP_400_BAD_REQUEST)

        code_data_raw = cache.get(f"auth_code:{code}")
        if not code_data_raw:
            return Response(
                {"error": "invalid_grant", "error_description": "Invalid or expired authorization code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code_data = json.loads(code_data_raw)

        if normalize_uri(redirect_uri) != normalize_uri(code_data["redirect_uri"]):
            return Response(
                {"error": "invalid_grant", "error_description": "Invalid redirect URI"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if code_data["used"]:
            return Response(
                {"error": "invalid_grant", "error_description": "Code already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code_data["used"] = True
        cache.set(f"auth_code:{code}", json.dumps(code_data), timeout=60)

        user = User.objects.get(id=code_data["user_id"])

        access_token = self._generate_access_token(user, client, code_data)
        refresh_token = self._generate_refresh_token(user, client, code_data)

        return Response(
            {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": int(settings.SSO.get("ACCESS_TOKEN_EXPIRATION").total_seconds()),
                "refresh_token": refresh_token,
            }
        )

    def _generate_access_token(self, user, client, code_data):
        payload = {
            "user_id": str(user.id),
            "client_id": client.client_id,
            "scopes": code_data["scopes"],
            "exp": now() + settings.SSO.get("ACCESS_TOKEN_EXPIRATION"),
        }
        return jwt.encode(payload, settings.SSO.get("JWT_SECRET_KEY"), algorithm="HS256")

    def _generate_refresh_token(self, user, client, code_data):
        token = secrets.token_urlsafe(64)
        timeout = settings.SSO.get("REFRESH_TOKEN_EXPIRATION").total_seconds()

        cache.set(
            f"refresh_token:{token}",
            {
                "user_id": str(user.id),
                "client_id": client.client_id,
                "scopes": code_data["scopes"],
                "exp": now() + settings.SSO.get("ACCESS_TOKEN_EXPIRATION"),
            },
            timeout=timeout,
        )

        return token


class UserInfoView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        token = self._get_token_from_request(request)
        if not token:
            return Response({"error": "missing_token"}, status=401)

        if cache.get(f"blacklisted_token:{token}"):
            return Response({"error": "token_revoked"}, status=401)

        try:
            payload = jwt.decode(token, settings.SSO["JWT_SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response({"error": "token_expired"}, status=401)
        except jwt.InvalidTokenError:
            return Response({"error": "invalid_token"}, status=401)

        user = User.objects.filter(id=payload["user_id"]).first()
        if not user:
            return Response({"error": "user_not_found"}, status=404)

        scopes = payload.get("scopes", [])

        data = {"sub": str(user.id)}
        if "email" in scopes:
            data["email"] = user.email
        if "profile" in scopes:
            data.update(
                {
                    "name": user.username,
                    "given_name": user.first_name,
                    "family_name": user.last_name,
                    "profile_picture": (
                        request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
                    ),
                }
            )

        return Response(data)

    def _get_token_from_request(self, request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split("Bearer ")[1]
        return None


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "missing_refresh_token"}, status=status.HTTP_400_BAD_REQUEST)

        refresh_token_data = cache.get(f"refresh_token:{refresh_token}")
        if not refresh_token_data:
            return Response(
                {"error": "invalid_grant", "error_description": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = refresh_token_data["user_id"]
        client_id = refresh_token_data["client_id"]
        scopes = refresh_token_data["scopes"]

        client = Application.objects.filter(client_id=client_id).first()
        if not client:
            return Response({"error": "invalid_client"}, status=status.HTTP_400_BAD_REQUEST)

        if refresh_token_data["exp"] < now():
            return Response({"error": "token_expired"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return Response({"error": "user_not_found"}, status=status.HTTP_404_NOT_FOUND)

        access_token = self._generate_access_token(user, client, scopes)
        new_refresh_token = self._generate_refresh_token(user, client, scopes)

        return Response(
            {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": int(settings.SSO.get("ACCESS_TOKEN_EXPIRATION").total_seconds()),
                "refresh_token": new_refresh_token,
            }
        )

    def _generate_access_token(self, user, client, scopes):
        """
        Generate the access token with scopes and expiration time.
        """
        payload = {
            "user_id": str(user.id),
            "client_id": client.client_id,
            "scopes": scopes,
            "exp": now() + settings.SSO.get("ACCESS_TOKEN_EXPIRATION"),
        }
        return jwt.encode(payload, settings.SSO.get("JWT_SECRET_KEY"), algorithm="HS256")

    def _generate_refresh_token(self, user, client, scopes):
        """
        Generate and cache a new refresh token.
        """
        token = secrets.token_urlsafe(64)
        timeout = settings.SSO.get("REFRESH_TOKEN_EXPIRATION").total_seconds()

        cache.set(
            f"refresh_token:{token}",
            {
                "user_id": str(user.id),
                "client_id": client.client_id,
                "scopes": scopes,
                "exp": now() + settings.SSO.get("REFRESH_TOKEN_EXPIRATION"),
            },
            timeout=timeout,
        )

        return token


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = self._get_token_from_request(request)
        if not token:
            return Response({"error": "missing_token"}, status=400)

        try:
            payload = jwt.decode(token, settings.SSO["JWT_SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response({"error": "token_expired"}, status=400)
        except jwt.InvalidTokenError:
            return Response({"error": "invalid_token"}, status=400)

        exp_timestamp = payload["exp"]
        ttl = exp_timestamp - int(now().timestamp())
        if ttl > 0:
            cache.set(f"blacklisted_token:{token}", "1", timeout=ttl)

        return Response(status=204)

    def _get_token_from_request(self, request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split("Bearer ")[1]
        return None


class LoginView(DJLoginView):
    template_name = "users/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_to = self.request.GET.get("next")
        if redirect_to and url_has_allowed_host_and_scheme(redirect_to, self.request.get_host()):
            return redirect_to

        return settings.LOGIN_REDIRECT_URL


class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = RegisterForm

    def form_valid(self, form):
        form.save()
        next_url = self.request.POST.get("next", "")
        login_url = reverse("accounts:login")
        if next_url and url_has_allowed_host_and_scheme(next_url, self.request.get_host()):
            login_url += f"?next={next_url}"
        return redirect(login_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "")
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["next"] = self.request.GET.get("next")
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"files": self.request.FILES})
        return kwargs
