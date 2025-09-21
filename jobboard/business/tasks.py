from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_email_notification(subject, message, recipient_list):
    """
    Celery task to send email notifications asynchronously.

    Behavior:
        - Uses Django's send_mail function with DEFAULT_FROM_EMAIL from setting as the sender.
        - Runs asynchronously via Celery.
        - Raises an exception if sending fails (fail_silently=False).
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
