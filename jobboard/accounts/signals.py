from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import VerificationRequest, User
from business.models import Notifications

@receiver(post_save, sender=VerificationRequest)
def notify_admins_on_request(sender, instance, created, **kwargs):
    """
    Signal: Triggered whenever a VerificationRequest is created.

    Behavior:
        - If a new request is created with status "pending":
            - Notify all admins by creating a Notifications object for each admin.
    """
    if created and instance.status == "pending":
        admins = User.objects.filter(role='admin')
        for admin in admins:
            Notifications.objects.create(
                recipient=admin,
                message=f"{instance.user.email} requested verification."
            )

@receiver(post_save, sender=VerificationRequest)
def notify_user_on_status_change(sender, instance, created, **kwargs):
    """
    Triggered whenever a VerificationRequest is updated.

    Behavior:
        - Ignores request creation (already handled for admins).
        - If status changes to "approved" or "denied":
            - Notify the requesting user with a status update.
    """
    if not created:
        if instance.status in ["approved", "denied"]:
            Notifications.objects.create(
                recipient=instance.user,
                message=f"Your verification request has been {instance.status}."
            )
