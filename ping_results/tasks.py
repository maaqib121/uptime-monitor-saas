from django.conf import settings
from pingApi.celery import app
from companies.models import Company
from companies.utils.common import send_ping_email, send_ping_sms
from datetime import datetime, timedelta
from pytz import timezone
from collections import namedtuple
import requests


@app.task(name='tasks.ping')
def ping(company_id):
    company = Company.objects.filter(id=company_id).first()
    if not company:
        return 'Company not Found.'

    for url in company.url_set.all():
        try:
            response = requests.get(
                url.url,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
            )
        except:
            response = namedtuple('Response', {'status_code': 200})(**{'status_code': 200})

        if response.status_code != 200 and (
            url.last_ping_status_code != response.status_code or
            url.last_ping_date_time is None or
            datetime.now(tz=timezone(settings.TIME_ZONE)) > url.last_ping_date_time + timedelta(days=1)
        ):
            send_ping_email(url, response.status_code)
            send_ping_sms(url, response.status_code)

        url.pingresult_set.create(status_code=response.status_code, company=url.company)
        url.set_last_ping_status_code(response.status_code)

    ping.apply_async((company_id,), countdown=1800)
    return f'All URLs of {company} have been pinged.'
