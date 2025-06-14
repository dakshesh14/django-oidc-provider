from django.urls import path

from .views import LogoutView, RefreshTokenView, TokenView, UserInfoView

app_name = "accounts"

urlpatterns = [
    path("token/", TokenView.as_view(), name="token"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token"),
    path("userinfo/", UserInfoView.as_view(), name="userinfo"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
