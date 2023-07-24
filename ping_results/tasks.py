from django.conf import settings
from pingApi.celery import app
from pingApi.constants import PING_INTERVAL_IN_SECONDS
from companies.models import Company
from companies.utils.common import send_ping_email, send_ping_sms
from datetime import datetime, timedelta
from pytz import timezone
from collections import namedtuple
import httpx


@app.task(name='tasks.ping')
def ping(company_id):
    company = Company.objects.filter(id=company_id).first()
    if not company:
        return 'Company not Found.'

    client = httpx.Client(http2=True)
    for domain in company.domain_set.all():
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

    return f'All URLs of {company} have been pinged.'
