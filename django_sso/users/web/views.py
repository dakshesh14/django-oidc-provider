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


class AuthorizeView(LoginRequiredMixin, View):
    login_url = "/users/login/"

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

        next_url = self.request.POST.get("next", "")
        login_url = reverse("accounts:web:login")
        if next_url and url_has_allowed_host_and_scheme(next_url, self.request.get_host()):
            login_url += f"?next={next_url}"
        return redirect(login_url)

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
