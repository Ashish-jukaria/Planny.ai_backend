from django.urls import path
from .views import *
from .Razorpay.razorpay_views import handle_payment_failure, handle_payment_success
from .gateways.razorpay.webhooks import webhook_receiver
from .api.views import Payment


urlpatterns = [
    # path('handle_payment_success/',handle_payment_success,name="handle_payment_success"),
    # path('handle_payment_failure/',handle_payment_failure,name="handle_payment_failure"),
    path(
        "checkout/<str:pk>/<str:delivery_type>/",
        Payment.as_view({"post": "checkout"}),
        name="payment_checkout",
    ),
    path("success/", Payment.as_view({"post": "success"}), name="success"),
    path("failure/", Payment.as_view({"post": "failure"}), name="failure"),
    path("webhook_receiver/", webhook_receiver, name="webhook_receiver"),
    # path('payments/',Payment.as_view()),
]


# from django.conf.urls import url, include
# from django.conf.urls.static import static
#
# urlpatterns = [
#     url(r'payments/', Payment.as_view())
# ]
