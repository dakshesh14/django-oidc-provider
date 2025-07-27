from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin

# django
from django.contrib.auth.views import LoginView as DJLoginView
from django.contrib.auth.views import PasswordResetCompleteView as DJPasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView as DJPasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView as DJPasswordResetDoneView
from django.contrib.auth.views import PasswordResetView as DJPasswordResetView
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.timezone import now
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django_sso.core.email.send_mail import send_mail

# form
from django_sso.users.forms import PasswordResetForm, RegisterForm, ResendVerificationForm

# local
# models
from django_sso.users.models import Application, User
from django_sso.users.utils.auth import create_and_cache_auth_code
from django_sso.users.utils.email_verification import generate_email_verification_token, verify_email_token

# utils
from django_sso.utils.string import normalize_uri


class AuthorizeView(View):
    def get(self, request, *args, **kwargs):
        client_id = request.GET.get("client_id")
        redirect_uri = request.GET.get("redirect_uri")
        state = request.GET.get("state", "")
        scope = request.GET.get("scope", "openid")
        response_type = request.GET.get("response_type", "code")
        nonce = request.GET.get("nonce")
        code_challenge = request.GET.get("code_challenge")
        code_challenge_method = request.GET.get("code_challenge_method")

        if response_type != "code":
            return self._error_redirect(redirect_uri, state, "unsupported_response_type")

        if "openid" in scope.split() and not nonce:
            return self._error_redirect(redirect_uri, state, "invalid_request")

        if not client_id or not redirect_uri:
            return self._error_redirect(redirect_uri, state, "invalid_request")

        client = Application.objects.filter(client_id=client_id, is_active=True).first()
        if not client:
            return self._error_redirect(redirect_uri, state, "invalid_client")

        if normalize_uri(redirect_uri) not in client.get_redirect_uris():
            return self._error_redirect(redirect_uri, state, "invalid_redirect_uri")

        requested_scopes = scope.split()
        allowed_scopes = set(client.get_allowed_scopes())
        granted_scopes = [s for s in requested_scopes if s in allowed_scopes]

        if not granted_scopes:
            return self._error_redirect(redirect_uri, state, "invalid_scope")

        request.session["oidc_context"] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": granted_scopes,
            "timestamp": now().isoformat(),
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        }

        if not request.user.is_authenticated:
            login_url = reverse("accounts:web:login")
            query_params = {
                "next": reverse("accounts:web:resume_authorization"),
            }
            login_url += f"?{urlencode(query_params)}"
            return redirect(login_url)

        return self._complete_authorization(request)

    def _is_session_expired(self, context):
        """Check if OIDC session context is expired (uses AUTH_CODE_TTL)"""
        if not context or "timestamp" not in context:
            return True

        from datetime import datetime, timedelta

        try:
            timestamp = datetime.fromisoformat(context["timestamp"])
            return now() > timestamp + timedelta(seconds=settings.AUTH_CODE_TTL)
        except (ValueError, TypeError):
            return True

    def _complete_authorization(self, request):
        context = request.session.pop("oidc_context", None)
        if not context:
            return redirect("/error?error=session_lost")

        if self._is_session_expired(context):
            return redirect("/error?error=session_expired")

        client_id = context["client_id"]
        redirect_uri = context["redirect_uri"]
        state = context.get("state", "")
        scope = context.get("scope", [])
        nonce = context.get("nonce")
        code_challenge = context.get("code_challenge")
        code_challenge_method = context.get("code_challenge_method")

        client = Application.objects.filter(client_id=client_id, is_active=True).first()
        if not client:
            return self._error_redirect(redirect_uri, state, "invalid_client")

        auth_code = create_and_cache_auth_code(
            request.user,
            client,
            redirect_uri,
            scope,
            nonce=nonce,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        query = urlencode({"code": auth_code, "state": state})
        return redirect(f"{redirect_uri}?{query}")

    def _error_redirect(self, redirect_uri, state, error_code):
        if redirect_uri:
            try:
                safe_redirect_uri = normalize_uri(redirect_uri)
                if url_has_allowed_host_and_scheme(safe_redirect_uri, allowed_hosts=None):
                    query = {"error": error_code}
                    if state:
                        query["state"] = state
                    return redirect(f"{safe_redirect_uri}?{urlencode(query)}")
            except Exception:
                pass

        return redirect(f"/error?error={error_code}")


class ResumeAuthorizationView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request, *args, **kwargs):
        oidc_context = request.session.get("oidc_context", None)
        if not oidc_context:
            return redirect("/error?error=session_lost")

        if self._is_session_expired(oidc_context):
            request.session.pop("oidc_context", None)
            return redirect("/error?error=session_expired")

        client_id = oidc_context.get("client_id")
        redirect_uri = oidc_context.get("redirect_uri")
        state = oidc_context.get("state", "")
        scope = oidc_context.get("scope", [])
        nonce = oidc_context.get("nonce", [])
        code_challenge = oidc_context.get("code_challenge", [])
        code_challenge_method = oidc_context.get("code_challenge_method", [])

        authorizer_url = reverse("accounts:web:authorize")
        query_params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(scope),
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        }
        authorizer_url += f"?{urlencode(query_params)}"
        return redirect(authorizer_url)

    def _is_session_expired(self, context):
        """Check if OIDC session context is expired (uses AUTH_CODE_TTL)"""
        if not context or "timestamp" not in context:
            return True

        from datetime import datetime, timedelta

        try:
            timestamp = datetime.fromisoformat(context["timestamp"])
            return now() > timestamp + timedelta(seconds=settings.AUTH_CODE_TTL)
        except (ValueError, TypeError):
            return True


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
        user = form.save(commit=False)
        user.email_verified = False
        user.save()

        token = generate_email_verification_token(user.id)
        self.send_verification_email(user, token)

        next_url = self.request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, self.request.get_host()):
            return redirect(next_url)

        return redirect(reverse("accounts:web:login"))

    def send_verification_email(self, user, token):
        """Send email verification email"""
        context = {
            "user": user,
            "token": token,
            "domain": self.request.get_host(),
            "protocol": "https" if self.request.is_secure() else "http",
        }

        subject = render_to_string("email/users/email_verification_subject.txt", context).strip()
        body = render_to_string("email/users/email_verification_email.html", context)
        send_mail.delay(subject, body, user.email)

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


class EmailVerificationView(TemplateView):
    template_name = "users/email_verification.html"

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        return self.render_to_response(
            {
                "token": token,
                "show_verification_form": True,
            }
        )

    def post(self, request, *args, **kwargs):
        token = kwargs.get("token")
        user_id = verify_email_token(token)

        if not token or not user_id:
            return self.render_to_response({"success": False, "user": None})

        try:
            user = User.objects.get(id=user_id)
            user.email_verified = True
            user.save(update_fields=["email_verified"])

            return self.render_to_response({"success": True, "user": user})
        except User.DoesNotExist:
            return self.render_to_response({"success": False, "user": None})


class ResendVerificationView(FormView):
    template_name = "users/resend_verification.html"
    form_class = ResendVerificationForm

    def get_success_url(self):
        return reverse("accounts:web:email_verification_sent")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.objects.get(email=email)

        if not user.email_verified:
            token = generate_email_verification_token(user.id)
            self.send_verification_email(user, token)

        return super().form_valid(form)

    def send_verification_email(self, user, token):
        """Send email verification email"""
        context = {
            "user": user,
            "token": token,
            "domain": self.request.get_host(),
            "protocol": "https" if self.request.is_secure() else "http",
        }

        subject = render_to_string("email/users/email_verification_subject.txt", context).strip()
        body = render_to_string("email/users/email_verification_email.html", context)
        send_mail.delay(subject, body, user.email)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "")
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["next"] = self.request.GET.get("next")
        return initial


class EmailVerificationSentView(TemplateView):
    template_name = "users/email_verification_sent.html"


class PasswordResetView(DJPasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "email/users/password_reset_email.html"
    subject_template_name = "email/users/password_reset_subject.txt"
    success_url = "/users/password-reset/done/"
    form_class = PasswordResetForm


class PasswordResetDoneView(DJPasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class PasswordResetConfirmView(DJPasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    form_class = SetPasswordForm
    success_url = "/users/reset/done/"


class PasswordResetCompleteView(DJPasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"
