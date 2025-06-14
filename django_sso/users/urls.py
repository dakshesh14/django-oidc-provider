from django.urls import include, path

app_name = "accounts"

urlpatterns = [
    path("users/", include(("django_sso.users.web.urls", "accounts"), namespace="web")),
    path("api/users/", include(("django_sso.users.api.urls", "accounts"), namespace="api")),
]
