from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from config import celery_app


@celery_app.task()
def send_mail(subject, html_content, to, attachments=None):
    try:
        text_content = strip_tags(html_content)
        from_email = settings.DEFAULT_FROM_EMAIL or "noreply@example.com"

        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [to],
            attachments=attachments,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
