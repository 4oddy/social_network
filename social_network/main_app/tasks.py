from first_site.celery_app import app

from django.core.mail import EmailMessage
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()


@app.task
def send_email(subject, body, to):
    """ Simple sending email """
    email = EmailMessage(subject=subject, body=body, to=to)
    email.send()


@app.task
def send_password_reset_email(subject_template_name, email_template_name, context,
                              from_email, to_email, html_email_template_name):
    """ Task to send password reset emails by Celery worker """

    context['user'] = User.objects.get(pk=context['user'])

    PasswordResetForm.send_mail(None, subject_template_name, email_template_name,
                                context, from_email, to_email, html_email_template_name)
