from django.shortcuts import render
from django.views import View
import os
from django.conf import settings
import logging
from account.models import Tenant

logger = logging.getLogger("phurti")


class DynamicTemplateView(View):
    def get_template_name(self, request):
        host = request.META.get("HTTP_HOST")
        subdomain, _, domain = host.partition(".")
        if domain == settings.COMPANY_URL:
            tenant = Tenant.objects.filter(subdomain=subdomain).first()
            if tenant:
                return os.path.join(settings.BASE_DIR, "frontend/theme/build/index.html")
            else:
                return os.path.join(settings.BASE_DIR, "frontend/phurti/build/index.html")
        else:
            return os.path.join(settings.BASE_DIR, "frontend/phurti/build/index.html")

    def get(self, request, *args, **kwargs):
        template_name = self.get_template_name(request)
        return render(request, template_name)
