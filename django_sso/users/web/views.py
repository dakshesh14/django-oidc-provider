from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin

# django
from django.contrib.auth.views import LoginView as DJLoginView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic.edit import FormView

# form
from django_sso.users.forms import RegisterForm

# local
# models
from django_sso.users.models import Application
from django_sso.users.utils.auth import create_and_cache_auth_code

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
