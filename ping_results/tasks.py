from pingApi.celery import app
from companies.models import Company
import requests


@app.task(name='tasks.ping')
def ping(company_id):
    company = Company.objects.filter(id=company_id).first()
    if not company:
        return 'Company not Found.'

    for url in company.url_set.all():
        response = requests.get(url.url)
        url.pingresult_set.create(status_code=response.status_code, company=url.company)
        url.set_last_ping_status_code(response.status_code)

    ping.apply_async((company_id,), countdown=1800)
    return f'All URLs of {company} have been pinged.'
