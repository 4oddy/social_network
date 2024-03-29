from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

from core.email.services import (EmailSenderNotifies, SenderNotifiesAggregator,
                                 TelegramSenderNotifies)
from first_site.celery_app import app

User = get_user_model()

sender_notifies = SenderNotifiesAggregator([EmailSenderNotifies(), TelegramSenderNotifies()])


@app.task
def send_email(subject: str, body: str, to: int) -> None:
    """ Simple sending email """
    receiver = User.objects.filter(pk=to).first()

    if receiver is not None:
        sender_notifies.send_notify(subject=subject, body=body, to=receiver)


@app.task
def send_password_reset_email(subject_template_name: str, email_template_name: str, context: dict,
                              from_email: str, to_email: str, html_email_template_name: str) -> None:
    """ Task to send password reset emails by Celery worker """

    context['user'] = User.objects.get(pk=context['user'])

    PasswordResetForm.send_mail(None, subject_template_name, email_template_name,
                                context, from_email, to_email, html_email_template_name)
