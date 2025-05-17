from django.urls import path

from .views import AuthorizeView, LoginView, LogoutView, RefreshTokenView, RegisterView, TokenView, UserInfoView

app_name = "accounts"

urlpatterns = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    # token related
    path("authorize/", AuthorizeView.as_view(), name="authorize"),
    path("token/", TokenView.as_view(), name="token"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token"),
    path("userinfo/", UserInfoView.as_view(), name="userinfo"),
]
