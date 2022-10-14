from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_confirmation_email(user, redirect_uri):
    message = render_to_string('emails/confirmation_email.html', {
        'user': user,
        'redirect_uri': redirect_uri,
        'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
        'token': user.confirmation_token,
    })
    mail = Mail(
        from_email=settings.SENDGRID_SENDER_EMAIL,
        to_emails=user.email,
        subject='Verify your new Ping-App account',
        html_content=message
    )
    try:
        send_grid = SendGridAPIClient(settings.SENDGRID_API_KEY)
        send_grid.send(mail)
    except:
        return Response(
            {'errors': {'non_field_errors': ['Could not send confirmation email to this email address.']}},
            status=status.HTTP_400_BAD_REQUEST
        )


def send_reset_password_email(user, redirect_uri):
    message = render_to_string('emails/reset_password_email.html', {
        'redirect_uri': redirect_uri,
        'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
        'token': user.confirmation_token,
    })
    mail = Mail(
        from_email=settings.SENDGRID_SENDER_EMAIL,
        to_emails=user.email,
        subject='Reset Ping-App Password',
        html_content=message
    )
    try:
        send_grid = SendGridAPIClient(settings.SENDGRID_API_KEY)
        send_grid.send(mail)
    except:
        return Response(
            {'errors': {'non_field_errors': ['Could not send confirmation email to this email address.']}},
            status=status.HTTP_400_BAD_REQUEST
        )
