from django.http import HttpResponse
from urllib.parse import urlparse
import csv
import xlwt


def export_to_csv(domain):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{urlparse(domain.domain_url).netloc}.csv"'
    writer = csv.writer(response)
    writer.writerow(['URL', 'Last Ping Status Code'])
    for url in domain.url_set.values_list('url', 'last_ping_status_code'):
        writer.writerow(url)
    return response


def export_to_xls(domain):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{urlparse(domain.domain_url).netloc}.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('URLs')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['URL', 'Last Ping Status Code']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = domain.url_set.values_list('url', 'last_ping_status_code')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response
