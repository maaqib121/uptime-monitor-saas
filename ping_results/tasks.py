from django.conf import settings
from pingApi.celery import app
from companies.models import Company
from companies.utils.common import send_ping_email, send_ping_sms
from datetime import datetime, timedelta
from pytz import timezone
from collections import namedtuple
import httpx


@app.task(name='tasks.ping')
def ping():
    for company in Company.objects.all():
        client = httpx.Client(http2=True)
        for domain in company.domain_set.filter(is_active=True):
            if not domain.is_subscription_active and company.remaining_trail_days < 0:
                continue

            urls = []
            for url in domain.url_set.filter(is_active=True):
                try:
                    response = client.get(url.url)
                except:
                    response = namedtuple('Response', {'status_code': 500})(**{'status_code': 500})

                ping_result = url.pingresult_set.create(status_code=response.status_code, company=url.company)
                if response.status_code < 200 and response.status_code > 399 and (
                    url.last_ping_status_code != response.status_code or
                    url.last_alert_date_time is None or
                    datetime.now(tz=timezone(settings.TIME_ZONE)) > url.last_alert_date_time + timedelta(days=1)
                ):
                    urls.append({'url': url, 'status_code': response.status_code})
                    url.set_last_alert_date_time(ping_result.created_at)

                url.set_last_ping_status_code(response.status_code)

            if urls:
                send_ping_email(domain, urls)
                send_ping_sms(domain)

    return f'All Ping Results have been stored successfully.'
