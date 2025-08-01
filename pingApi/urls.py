"""pingApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('countries.urls')),
    path('', include('companies.urls')),
    path('', include('users.urls')),
    path('', include('plans.urls')),
    path('', include('payment_methods.urls')),
    path('', include('invoices.urls')),
    path('', include('domains.urls')),
    path('', include('ping_results.urls')),
    path('webhooks/', include('webhooks.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Takemint Admin'
admin.site.index_title = 'Admin'
admin.site.site_title = 'Takemint'
