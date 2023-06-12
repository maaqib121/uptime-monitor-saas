from django.conf import settings
import requests


def get_company_google_access_token(company):
    response = requests.post(
        url='https://oauth2.googleapis.com/token',
        data={
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'refresh_token': company.google_refresh_token,
            'grant_type': 'refresh_token'
        }
    )
    if response.status_code != 200:
        company.clear_linked_google_account()
    else:
        return response.json()['access_token']
