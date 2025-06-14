from django.urls import path

from .views import AuthorizeView, LoginView, RegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("authorize/", AuthorizeView.as_view(), name="authorize"),
]
