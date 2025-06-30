from django.urls import path

from .views import (
    AuthorizeView,
    EmailVerificationSentView,
    EmailVerificationView,
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
    RegisterView,
    ResendVerificationView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("authorize/", AuthorizeView.as_view(), name="authorize"),
    # email verification flow
    path("verify-email/<str:token>/", EmailVerificationView.as_view(), name="email_verification"),
    path("resend-verification/", ResendVerificationView.as_view(), name="resend_verification"),
    path("email-verification-sent/", EmailVerificationSentView.as_view(), name="email_verification_sent"),
    # password reset flow
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
