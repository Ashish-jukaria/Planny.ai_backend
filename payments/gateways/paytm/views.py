import requests
import json
from payments.gateways.base import BaseGateway
from payments.constants import *
from rest_framework.response import Response
from rest_framework import status
import phurti.settings as settings
from payments.constants import *
from phurti.constants import *

# import paytmchecksum
from .utils import *
from notifications.views import *
from shop.models import *
from django.utils import timezone
from shop.views import *

payment_code = {"CC": CARD, "DC": CARD, "NB": NETBANKING, "UPI": UPI, "PPI": WALLET}


class PAYTMGateway(BaseGateway):
    def get_payment_source(self):
        return PAYTM

    def get_success_status(self):
        return PAYMENT_SUCCESS

    def get_failure_status(self):
        return PAYMENT_FAILED

    def success(self, request):
        data = request.data["response"]
        order_id = str(request.data["order_id"])
        try:
            order = Order.objects.filter(pk=int(order_id.strip())).first()
        except:
            return Response(
                {
                    "message": "Order not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction_details = transaction_detail(order_id)
        body = {"mid": settings.PAYTM_MERCHANT_ID, "orderId": order_id}
        paytmChecksum = data["CHECKSUMHASH"]
        # isVerifySignature = paytmchecksum.verifySignature(body, settings.PAYTM_MERCHANT_KEY, paytmChecksum)

        payment = Payment.objects.filter(order=order).first()

        # Updating Payment Details"
        payment.status = SUCCESS
        payment.payment_id = data["TXNID"]
        payment.payment_date = str(timezone.now())
        payment.mode = payment_code[data["PAYMENTMODE"]]
        payment.additional_details = json.dumps(transaction_details["body"])
        payment.save()

        # Updating Order Details
        order.mode_of_payment = payment_code[data["PAYMENTMODE"]]
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

    def failure(self, request):
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

        transaction_details = transaction_detail(order_id)
        # paytm Details

        # Updating Payment Details
        payment = Payment.objects.filter(order=order).first()
        payment.status = FAILED
        payment.payment_id = data["TXNID"]
        payment.mode = payment_code[data["PAYMENTMODE"]]
        payment.payment_date = str(timezone.now())
        payment.additional_details = json.dumps(transaction_details["body"])
        payment.save()
        print("Payment Updated")

        # Updating Order Details
        order.mode_of_payment = payment_code[data["PAYMENTMODE"]]
        order.payment_status = FAILED
        order.status = FAILED
        order.save()
        print("Order Updated")

        return Response(
            {"message": "Payment Unsuccessful", "order_id": order_id},
            status=status.HTTP_200_OK,
        )


class View:
    def __init__(self):
        self.gateway = PAYTMGateway


view = View()
