from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from .models import JoinRequest, Invitation

@receiver(post_save, sender=JoinRequest)
def notify_admins_on_join_request(sender, instance, created, **kwargs):
    """
    When a JoinRequest is created, notify all owners/admins by email.
    """
    if not created:
        return
    family = instance.family
    recipients = [
        m.user.email for m in family.memberships.filter(role__in=['owner', 'admin']).select_related('user') if m.user.email
    ]
    if not recipients:
        return

    context = {'family': family, 'requester': instance.user, 'message': instance.message}
    subject = f'New join request for {family.name}'
    text = render_to_string('families/emails/join_request.txt', context)
    html = render_to_string('families/emails/join_request.html', context)
    send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, recipients, html_message=html, fail_silently=True)

@receiver(post_save, sender=Invitation)
def notify_invited_user(sender, instance, created, **kwargs):
    """
    Optionally send a follow-up email when an Invitation is created.
    (Invitation creation currently triggers email in the view; this is a fallback.)
    """
    if not created:
        return
    if not instance.email:
        return
    # If you already send email in the view, you can remove this handler.
    # Keep here as a fallback only.
    try:
        accept_url = instance.token  # token will be set by the view before saving
        subject = f"You're invited to join {instance.family.name}"
        context = {'family': instance.family, 'inviter': instance.inviter, 'accept_url': accept_url}
        text = render_to_string('families/emails/invitation.txt', context)
        html = render_to_string('families/emails/invitation.html', context)
        send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [instance.email], html_message=html, fail_silently=True)
    except Exception:
        pass
