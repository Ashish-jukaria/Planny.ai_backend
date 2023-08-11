from django.urls import path
from .views import *

urlpatterns = [
    path(
        "fetchorders/<int:offset>/<str:status>/<str:paymentStatus>/",
        fetch_orders.as_view(),
        name="fetchOrders",
    ),  # Login View
    path("updatepaymentmode/", update_payment_mode, name="fetchOrders"),
    path(
        "fetchexecutives/<str:inventory>/", fetch_executives, name="fetchExecutives"
    ),  # Login View
    path("assignorders/", assignOrders, name="assignOrders"),  # Login View
    path("updateorder/", update_order, name="updateOrder"),  # Login View
    path("getuserdetails/<int:id>/", get_user_details, name="getUserDetails"),
    path("logout/", logout_user, name="logout"),
]
