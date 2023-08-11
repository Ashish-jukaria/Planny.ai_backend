from account.models import Tenant
from django.conf import settings
# from urllib.parse import urlparse
# import os


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get("HTTP_HOST")
        subdomain, _, domain = host.partition(".")
        if domain == settings.COMPANY_URL:
            tenant = Tenant.objects.filter(subdomain=subdomain).first()
            request.tenant_id = (
                tenant.id if tenant else settings.DEFAULT_TENANT_ID
            )
        else:
            tenant = Tenant.objects.filter(custom_domain=domain).first()
            request.tenant_id = (
                tenant.id if tenant else settings.DEFAULT_TENANT_ID
            )
        response = self.get_response(request)
        return response
