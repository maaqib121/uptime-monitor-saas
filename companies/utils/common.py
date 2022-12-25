from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.conf import settings
from users.models import User
from postmarker.core import PostmarkClient
from twilio.rest import Client


def send_quotation_email(user, allowed_users, allowed_domains, allowed_urls, ping_interval, body):
    message = render_to_string('emails/quotation_email.html', {
        'user': user,
        'allowed_users': allowed_users,
        'allowed_domains': allowed_domains,
        'allowed_urls': allowed_urls,
        'ping_interval': ping_interval,
        'body': body
    })
    try:
        postmark = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
        postmark.emails.send(
            From=settings.POSTMARK_SENDER_EMAIL,
            To=settings.ADMIN_EMAIL,
            Subject=f'Quotation from {user.company}',
            HtmlBody=message
        )
    except:
        return Response(
            {'errors': {'non_field_errors': ['Could not send quotation email.']}},
            status=status.HTTP_400_BAD_REQUEST
        )


def send_ping_email(domain, urls):
    subject = f'Alert for {domain}'
    postmark = PostmarkClient(server_token=settings.POSTMARK_SERVER_TOKEN)
    for user in domain.users.all():
        try:
            message = render_to_string('emails/ping_email.html', {'user': user, 'domain': domain, 'urls': urls})
            postmark.emails.send(From=settings.POSTMARK_SENDER_EMAIL, To=user.email, Subject=subject, HtmlBody=message)
        except Exception as exception:
            print(exception)


def send_ping_sms(domain, urls):
    message = f'There is a problem in following urls of domain {domain}\n'
    for url in urls:
        message = f"{message}\n{url['url']}\n({url['status_code']})"
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    for user in domain.users.filter(is_phone_verified=True):
        try:
            client.messages.create(body=message, to=user.phone_number, from_=settings.TWILIO_SENDER_PHONE_NO)
        except Exception as exception:
            print(exception)
