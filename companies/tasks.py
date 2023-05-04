from pingApi.celery import app
from companies.models import Company
from companies.utils.generate_google_access_token import get_company_google_access_token
from urllib.parse import urlparse
import requests


@app.task(name='tasks.sync_google_analytics_domains')
def sync_google_analytics_domains():
    for company in Company.objects.filter(linked_google_email__isnull=False):
        google_access_token = get_company_google_access_token(company)
        accounts_response = requests.get(
            'https://www.googleapis.com/analytics/v3/management/accounts',
            headers={'Authorization': f'Bearer {google_access_token}'}
        )
        if accounts_response.status_code != 200:
            continue

        for account in accounts_response.json()['items']:
            web_properties_response = requests.get(
                f"https://www.googleapis.com/analytics/v3/management/accounts/{account['id']}/webproperties",
                headers={'Authorization': f'Bearer {google_access_token}'}
            )
            if web_properties_response.status_code != 200:
                continue

            for web_property in web_properties_response.json()['items']:
                uri = urlparse(web_property['websiteUrl'])
                company.domain_set.get_or_create(domain_url=f'{uri.scheme}://{uri.netloc}')

    return 'Domains have been synced with Google Analytics successfully.'
