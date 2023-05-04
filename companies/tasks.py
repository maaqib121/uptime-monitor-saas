from pingApi.celery import app
from companies.models import Company
from companies.utils.sync_google_analytics import sync_domains_from_google_analytics_account


@app.task(name='tasks.sync_google_analytics_domains')
def sync_google_analytics_domains():
    for company in Company.objects.filter(linked_google_email__isnull=False):
        sync_domains_from_google_analytics_account(company)
    return 'Domains have been synced with Google Analytics successfully.'


@app.task(name='tasks.sync_company_google_analytics_domains')
def sync_company_google_analytics_domains(company_id):
    company = Company.objects.filter(id=company_id).first()
    if not company:
        return 'Company not found.'
    sync_domains_from_google_analytics_account(company)
    return 'Domains have been synced with Google Analytics successfully.'
