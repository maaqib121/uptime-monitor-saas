from pingApi.celery import app
from companies.models import Company
from companies.utils.sync_google_analytics import sync_from_google_analytics_account


@app.task(name='tasks.sync_google_analytics')
def sync_google_analytics():
    for company in Company.objects.filter(linked_google_email__isnull=False):
        sync_from_google_analytics_account(company)
    return 'Domains have been synced with Google Analytics successfully.'


@app.task(name='tasks.sync_company_google_analytics')
def sync_company_google_analytics(company_id):
    company = Company.objects.filter(id=company_id).first()
    if not company:
        return 'Company not found.'
    sync_from_google_analytics_account(company)
    return 'Domains have been synced with Google Analytics successfully.'
