from django.conf import settings
import requests


def get_user_google_access_token(user):
    return requests.post(
        url='https://oauth2.googleapis.com/token',
        data={
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'refresh_token': user.google_refresh_token,
            'grant_type': 'refresh_token'
        }
    ).json()['access_token']
