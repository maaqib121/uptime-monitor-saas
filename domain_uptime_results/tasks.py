from pingApi.celery import app
from domains.models import Domain
from domain_uptime_results.models import DomainUptimeResult
from collections import namedtuple
from urllib.parse import urlparse
from datetime import datetime
import ssl
import socket
import httpx
import time


@app.task(name='tasks.get_domain_uptime_results')
def get_domain_uptime_results():
    for domain in Domain.objects.filter(is_active=True):
        client = httpx.Client(http2=True)
        try:
            start_time = time.time()
            response = client.get(domain.domain_url)
            end_time = time.time()
        except:
            end_time = time.time()
            response_data = {'status_code': 500}
            response = namedtuple('Response', response_data)(**response_data)

        elapsed_time = end_time - start_time

        if response.status_code >= 200 and response.status_code <= 399:
            domain_uptime_status = DomainUptimeResult.Status.UP
        else:
            domain_uptime_status = DomainUptimeResult.Status.DOWN

        domain_uptime_result = DomainUptimeResult(
            status=domain_uptime_status,
            status_code=response.status_code,
            response_time=elapsed_time,
            domain=domain,
            company=domain.company
        )
        if domain_uptime_result.status == DomainUptimeResult.Status.UP:
            context = ssl.create_default_context()
            hostname = urlparse(domain.domain_url).netloc
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    ssl_info = ssock.getpeercert()
                    domain_uptime_result.ssl_validity = datetime.strptime(ssl_info['notAfter'], '%b %d %H:%M:%S %Y %Z')

        domain_uptime_result.save()

    return 'All Domain Uptime Results have been stored successfully.'
