from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from payments.api.views import Payment
from .viewset import DynamicTemplateView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/account/", include("account.urls")),
    path("api/customer/", include("customer.urls")),
    path("api/contactus/", include("contactus.urls")),
    path("api/shop/", include("shop.urls")),
    path("api/operations/", include("operations.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/plan/", include("plan.urls")),

    # path("api/payments/", Payment)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += i18n_patterns(
#  url(r'^{}/'.format(settings.DJANGO_ADMIN_URL), admin.site.urls)
# )
urlpatterns.append(url(r"^(?:.*)/?$", DynamicTemplateView.as_view(), name="DynamicTemplateView"))


admin.site.site_header = "Aik-Tech India"
admin.site.site_title = "Aik-Tech India"
