from first_site.celery_app import app

from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


@app.task
def send_email(subject, body, to):
    email = EmailMessage(subject=subject, body=body, to=to)
    email.send()


@app.task
def send_email_for_all(subject, body):
    if settings.SEND_EMAILS:
        users = User.objects.all()
        email = EmailMessage(subject=subject, body=body, to=[user.email for user in users])
        email.send()
