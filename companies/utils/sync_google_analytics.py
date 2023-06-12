from pingApi.constants import LANDING_PAGES_TO_RETRIEVE
from companies.utils.generate_google_access_token import get_company_google_access_token
from urls.models import Url
from urllib.parse import urlparse
import requests
import json


def sync_from_google_analytics_account(company):
    google_access_token = get_company_google_access_token(company)
    accounts_response = requests.get(
        'https://www.googleapis.com/analytics/v3/management/accounts',
        headers={'Authorization': f'Bearer {google_access_token}'}
    )
    if accounts_response.status_code == 200:
        for account in accounts_response.json()['items']:
            web_properties_response = requests.get(
                url=f'https://www.googleapis.com/analytics/v3/management/accounts/{account["id"]}/webproperties',
                headers={'Authorization': f'Bearer {google_access_token}'}
            )

            for web_property in web_properties_response.json()['items']:
                uri = urlparse(web_property['websiteUrl'])
                domain, _ = company.domain_set.get_or_create(domain_url=f'{uri.scheme}://{uri.netloc}')
                profiles_response = requests.get(
                    url=f"https://www.googleapis.com/analytics/v3/management/accounts/{account['id']}/webproperties/{web_property['id']}/profiles",
                    headers={'Authorization': f'Bearer {google_access_token}'})

                landing_pages = []
                for profile in profiles_response.json()['items']:
                    report_response = requests.post(
                        url='https://analyticsreporting.googleapis.com/v4/reports:batchGet',
                        headers={'Authorization': f'Bearer {google_access_token}'},
                        data=json.dumps({
                            'reportRequests': [
                                {
                                    'viewId': profile['id'],
                                    'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
                                    'metrics': [{'expression': 'ga:entrances'}],
                                    'dimensions': [{'name': 'ga:landingPagePath'}],
                                    'orderBys': [{'fieldName': 'ga:entrances', 'sortOrder': 'DESCENDING'}],
                                    'pageSize': 100
                                }
                            ]
                        })
                    )

                    for row in report_response.json()['reports'][0]['data'].get('rows', []):
                        landing_pages.append({'url': row['dimensions'][0], 'score': row['metrics'][0]['values'][0]})

                unique_landing_pages = {d['url']: d for d in landing_pages}.values()
                top_landing_pages = sorted(
                    unique_landing_pages,
                    key=lambda x: x['score'],
                    reverse=True
                )[:LANDING_PAGES_TO_RETRIEVE]

                url_ids = []
                urls = []
                for landing_page in top_landing_pages:
                    url, created = domain.url_set.get_or_create(url=f'{domain.domain_url}{landing_page["url"]}', company=company)
                    url_ids.append(url.id)
                    if not created and not url.is_active:
                        urls.append(Url(id=url.id, is_active=True))

                Url.objects.bulk_update(urls, fields=['is_active'])
                domain.url_set.exclude(id__in=url_ids).update(is_active=False)
