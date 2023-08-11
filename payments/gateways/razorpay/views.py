from notifications.views import send_order_communication
from phurti.constants import *
from payments.gateways.base import BaseGateway
from rest_framework import status
from datetime import datetime
import json
from shop.constants import WEBSITE
from webbrowser import get
from django.shortcuts import render
from payments.views import basePayment
from shop.models import Cart, Order, Payment
from rest_framework.response import Response
import razorpay
from django.http.response import HttpResponse
import logging
from shop.views import VoiceOTPsend, OTPsend, update_inventory
import phurti.settings as settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from payments.constants import *
from shop.models import *
from pyfcm import FCMNotification
from django.db.models import Q

push_service = FCMNotification(api_key=settings.FCM_API_KEY)

logger = logging.getLogger("phurti")


class RAZORPAYGateway(BaseGateway):
    def get_payment_source(self):
        return RAZORPAY

    def get_success_status(self):
        return PAYMENT_SUCCESS

    def get_failure_status(self):
        return PAYMENT_FAILED

    def success(self, request):
        # response_data = {
        #     "status": "SOME STATUS HERE"
        # }

        data = request.data["response"]
        order_id = request.data["order_id"]

        try:
            order = Order.objects.filter(pk=order_id).first()
        except:
            return Response(
                {
                    "message": "Order not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        razorpay_payment_id = data["razorpay_payment_id"]
        params_dict = {
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"],
        }
        # Verifying if request is from Razorpay
        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY)
            )
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
        payment = Payment.objects.filter(order=order).first()

        # Updating Payment Details"
        payment.status = SUCCESS
        payment.payment_id = data["razorpay_payment_id"]
        payment.payment_date = str(timezone.now())
        payment.mode = resp["method"]
        payment.additional_details = json.dumps(resp)
        payment.save()

        # Updating Order Details
        order.mode_of_payment = resp["method"]
        order.payment_status = SUCCESS
        order.status = ORDER_PLACED
        order.save()

        try:
            update_inventory(order)
        except Exception as e:
            logger.error(e)

        # Updating Cart details and removing the cart
        cart = Cart.objects.filter(customer=order.customer).last()
        cart.cartitem.all().update(is_active=False)
        cart.status = ORDER_PLACED
        cart.save()

        # Send OTP
        try:
            # VoiceOTPsend(settings.VOICE_PHONES)
            # OTPsend(settings.PHONES)
            # Sending notification to storemanager and admins for new order
            users = Profile.objects.filter(
                Q(inventory=request.user.inventory, role="SK") | Q(role="ADMIN")
            )
            device_ids = []
            for user in users:
                device_ids.append(user.device_id)
            message_title = "New Order"
            message_body = "You have a new order"
            extra_notification_kwargs = {
                "sound": "notification.wav",
                "android_channel_id": "hello",
            }
            result = push_service.notify_multiple_devices(
                registration_ids=device_ids,
                message_title=message_title,
                message_body=message_body,
                extra_notification_kwargs=extra_notification_kwargs,
            )

        except Exception as err:
            logger.error(str(err))

        # Send Order Confirmation message
        if settings.MESSAGE_SEND:
            send_order_communication(order, payment)

        return Response(
            {"message": "Payment Successful", "order_id": order_id},
            status=status.HTTP_200_OK,
        )
        # return Response(response_data, status=status.HTTP_200_OK)

    def failure(self, request):
        # response_data = {
        #     "status": "SOME STATUS HERE"
        # }

        data = request.data["response"]
        order_id = request.data["order_id"]
        print(data["error"])
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

        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY)
            )
        except:
            Response(
                {"Message": "Razorpay Server Down.. Try Again Later"},
                status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
            )

        # Razorpay Details
        razorpay_payment_id = data["error"]["metadata"]["payment_id"]
        resp = client.payment.fetch(razorpay_payment_id)
        print(resp)

        # Updating Payment Details
        payment = Payment.objects.filter(order=order).first()
        payment.status = FAILED
        payment.payment_id = razorpay_payment_id
        payment.mode = resp["method"]
        payment.payment_date = str(timezone.now())
        payment.additional_details = json.dumps(resp)
        payment.save()
        print("Payment Updated")

        # Updating Order Details
        order.mode_of_payment = resp["method"]
        order.payment_status = FAILED
        order.status = FAILED
        order.save()
        print("Order Updated")

        return Response(
            {"message": "Payment Unsuccessful", "order_id": order_id},
            status=status.HTTP_200_OK,
        )
        # return Response(response_data, status=status.HTTP_200_OK)


class View:
    def __init__(self):
        self.gateway = RAZORPAYGateway


view = View()
