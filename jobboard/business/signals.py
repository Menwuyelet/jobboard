from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Applications, Notifications
from .tasks import send_email_notification

@receiver(post_save, sender=Applications)
def create_notification_for_job_owner(sender, instance, created, **kwargs):
    """Create a notification for the job owner when a new application is submitted."""
    if created:  # only run when a new application is created
        Notifications.objects.create(
            application=instance,  # pass the object, not just ID
            recipient=instance.job.posted_by,
            message=f"{instance.user} applied to your job: {instance.job.title}",
        )

    if not created:
        if instance.status == "Accepted":
            Notifications.objects.create(
                application=instance, 
                recipient=instance.user,
                message=(
                    f"Your application for the job: {instance.job.title} has been reviewed. "
                    "The job owner accepted your application. Please wait for an email with further details. "
                    "Thank you!"
                ),
            )
            # Send email notification
            send_email_notification.delay(
                subject="Job Application Result",
                message=(
                    f"Dear {getattr(instance.user, 'username', instance.user)},\n\n"
                    f"🎉 Congratulations! You have been accepted for the job "
                    f"**{instance.job.title}** you applied for on {instance.applied_at}.\n\n"
                    "Please wait patiently for the job owner to contact you.\n\n"
                    "Thanks for choosing our platform!"
                ),
                # recipient_list=['menutemesgen@gmail.com',],
                recipient_list=[instance.user.email] if instance.user.email else [],
            )
            send_email_notification.delay(
                    subject=f"You accepted the application of {getattr(instance.user, 'username', instance.user)} for the your job {instance.job} post.",
                    message=(
                        f"Hello {getattr(instance.job.posted_by, 'username', instance.job.posted_by)},\n\n"
                        f"You have accepted the application of {getattr(instance.user, 'username', instance.user)} "
                        f"for your job: **{instance.job.title}**.\n\n"
                        f"Applicant details:\n"
                        f"- Name: {getattr(instance.user, 'username', instance.user)}\n"
                        f"- Email: {instance.user.email}\n"
                        f"- Applied at: {instance.applied_at}\n\n"
                        "Please reach out to the applicant to proceed further.\n\n"
                        "Thank you for using our platform!"
                    ),
                    recipient_list=[instance.job.posted_by.email] if instance.job.posted_by.email else [],
                )
            
        elif instance.status == "Rejected":
            # Create in-app notification
            Notifications.objects.create(
                application=instance,
                recipient=instance.user,
                message=(
                    f"Your application for the job: {instance.job.title} has been reviewed. "
                    "The job owner rejected your application. We encourage you to explore other jobs. "
                    "Thank you for using our platform!"
                ),
            )
            print('notfic')
            # Send rejection email
            send_email_notification.delay(
                subject="Job Application Result: Rejected",
                message=(
                    f"Dear {getattr(instance.user, 'username', instance.user)},\n\n"
                    f"Unfortunately, your application for the job **{instance.job.title}** "
                    f"submitted on {instance.applied_at} was not accepted.\n\n"
                    "We encourage you to explore other opportunities on our platform.\n\n"
                    "Thank you for using our platform!"
                ),
                # recipient_list=['menutemesgen@gmail.com',],
                recipient_list=[instance.user.email] if instance.user.email else [],
            ) 