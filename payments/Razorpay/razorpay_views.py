from datetime import datetime
import json
from shop.constants import WEBSITE
from webbrowser import get
from django.shortcuts import render
from payments.views import basePayment
from phurti.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from shop.models import Cart, Order, Payment
from rest_framework.response import Response
import razorpay
from django.http.response import HttpResponse
import logging
from shop.views import VoiceOTPsend, OTPsend
import phurti.settings as settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

logger = logging.getLogger("phurti")

# Create your views here.


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def handle_payment_success(request):
    print("Entered payment success")
    data = request.data["response"]
    order_id = request.data["order_id"]

    try:
        order = Order.objects.filter(pk=order_id).first()
    except:
        return Response(
            {
                "message": "Order not found",
            }
        )

    # Updating Cart details and removing the cart
    cart = Cart.objects.filter(customer=order.customer).last()
    cart.cartitem.all().update(is_active=False)
    cart.status = "ORDER_PLACED"
    print(cart.id)
    print(cart.status)
    cart.save()

    order_amount = order.total_price
    razorpay_payment_id = data["razorpay_payment_id"]
    params_dict = {
        "razorpay_order_id": data["razorpay_order_id"],
        "razorpay_payment_id": data["razorpay_payment_id"],
        "razorpay_signature": data["razorpay_signature"],
    }
    # Verifying if request is from Razorpay
    try:
        client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))
        check_payment = client.utility.verify_payment_signature(params_dict)
    except:
        Response(
            {"Message": "Razorpay Server Down.. Try Again Later"},
            status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
        )

    if check_payment is not None:
        return Response(
            {"message": "Something went wrong... Try again"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Fetching Razorpay Details
    resp = client.payment.fetch(razorpay_payment_id)

    # Capturing payment
    # try:
    #     res = client.payment.capture(razorpay_payment_id,order_amount*100,{"currency":"INR"})
    # except:
    #     return Response({"message":"Payment not recieved.. Try again","order_details":resp},status=status.HTTP_200_OK)

    # Linking Payment to Order
    payment = Payment.objects.create(order=order)

    # Updating Payment Details"
    payment.amount = order.total_price
    payment.payment_status = "SUCCESS"
    payment.payment_id = data["razorpay_payment_id"]
    payment.source = WEBSITE
    payment.gateway_type = "Razorpay"
    payment.payment_date = str(timezone.now())
    payment.mode = resp["method"]
    payment.additional_details = json.dumps(resp)
    payment.save()

    # Updating Order Details
    order.mode_of_payment = resp["method"]
    order.payment_status = "SUCCESS"
    order.save()

    try:
        VoiceOTPsend(settings.VOICE_PHONES)
        OTPsend(settings.PHONES)
    except Exception as err:
        logger.error(str(err))
    return Response(
        {"message": "Payment Successful", "order_details": resp, "order_id": order_id}
    )


@api_view(["POST"])
def handle_payment_failure(request):
    data = request.data["response"]
    order_id = request.data["order_id"]
    print(type(data["error"]))
    try:
        order = Order.objects.filter(pk=order_id).first()
    except:
        return Response(
            {
                "message": "Order not found",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Updating Payment Details
    payment = Payment.objects.create(order=order)
    payment.amount = order.total_price
    payment.payment_status = "FAILED"
    payment.payment_id = data["error"]["metadata"]["payment_id"]
    payment.source = WEBSITE
    payment.gateway_type = "Razorpay"
    payment.additional_details = json.dumps(data)
    payment.save()
    print("Payment Updated")
    # Updating Order Details
    order.payment_status = "FAILED"
    order.save()
    print("Order Updated")

    return Response(
        {"message": "Payment Unsuccessful", "order_id": order_id},
        status=status.HTTP_200_OK,
    )
