from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.conf import settings
from postmarker.core import PostmarkClient


def send_quotation_email(user, allowed_users, allowed_domains, allowed_urls, body):
    message = render_to_string('emails/quotation_email.html', {
        'user': user,
        'allowed_users': allowed_users,
        'allowed_domains': allowed_domains,
        'allowed_urls': allowed_urls,
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
