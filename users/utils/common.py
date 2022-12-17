from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from postmarker.core import PostmarkClient
from twilio.rest import Client


def send_confirmation_email(user, redirect_uri):
    message = render_to_string('emails/confirmation_email.html', {
        'user': user,
        'redirect_uri': redirect_uri,
        'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
        'token': user.confirmation_token,
    })
    try:
        postmark = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
        postmark.emails.send(
            From=settings.POSTMARK_SENDER_EMAIL,
            To=user.email,
            Subject='Verify your new TakeMint account',
            HtmlBody=message
        )
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
    try:
        postmark = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
        postmark.emails.send(
            From=settings.POSTMARK_SENDER_EMAIL,
            To=user.email,
            Subject='Reset your TakeMint Password',
            HtmlBody=message
        )
    except:
        return Response(
            {'errors': {'non_field_errors': ['Could not send confirmation email to this email address.']}},
            status=status.HTTP_400_BAD_REQUEST
        )


def send_set_password_email(user, redirect_uri):
    message = render_to_string('emails/set_password_email.html', {
        'user': user,
        'redirect_uri': redirect_uri,
        'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
        'token': user.confirmation_token,
    })
    try:
        postmark = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
        postmark.emails.send(
            From=settings.POSTMARK_SENDER_EMAIL,
            To=user.email,
            Subject='Set your TakeMint Password',
            HtmlBody=message
        )
    except:
        return Response(
            {'errors': {'non_field_errors': ['Could not send confirmation email to this email address.']}},
            status=status.HTTP_400_BAD_REQUEST
        )


def send_otp_sms(user, otp, phone_number=None):
    phone_number = phone_number if phone_number is not None else user.phone_number
    message = (
        f'{otp} is your One Time Password (OTP) for verification. Do not share this password with anyone.\n'
        'OTP will expire within 10 minutes.'
    )
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        client.messages.create(body=message, to=phone_number, from_=settings.TWILIO_SENDER_PHONE_NO)
    except Exception as exception:
        print(exception)
        return Response(
            {'errors': {'non_field_errors': ['Could not send OTP text to this phone number.']}},
            status=status.HTTP_400_BAD_REQUEST
        )
