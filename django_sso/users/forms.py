from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm as DJPasswordResetForm
from django.forms import EmailField
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

# local
from django_sso.core.email.send_mail import send_mail

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class RegisterForm(admin_forms.UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "username",
            "password1",
            "password2",
        )


class PasswordResetForm(DJPasswordResetForm):
    def send_mail(
        self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None
    ):
        """
        Override this to send a custom email.
        """
        subject = render_to_string(subject_template_name, context).strip()
        body = render_to_string(email_template_name, context)

        send_mail.delay(subject, body, to_email)
