from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication, permissions
from notifications.views import send_order_communication
from payments.constants import *
import phurti.settings as settings
from shop.views import VoiceOTPsend, OTPsend, update_inventory
from shop.constants import *
from shop.models import Cart, DeliveryType, Order, OrderItem, Payment as PaymentModel
from shop.serializers import OrderSerializer
from shop.utils import *
from .serializers import PaymentSerializer
from payments import gateways
from django.db import transaction
from decimal import Decimal
import logging
import razorpay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from shop.models import *
from pyfcm import FCMNotification
from payments.gateways.paytm.utils import *
from phurti.decorators.inventory_active import *

push_service = FCMNotification(api_key=settings.FCM_API_KEY)
logger = logging.getLogger("phurti")
DISCOUNT_SETTINGS = settings.DISCOUNT_SETTINGS


def get_payment_mode(order_id):
    payment_mode = settings.PAYMENT_TOGGLER
    payment_split_count = 0
    modes = []
    for mode in payment_mode:
        if payment_mode[mode]:
            payment_split_count += 1
            modes.append(mode)
    return modes[order_id % payment_split_count] if payment_split_count else False


class Payment(viewsets.ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    permissions_classes = (IsAuthenticated,)
    # authentication_classes = ()

    @action(methods=["POST"], detail=False)
    def checkout(self, request, *args, **kwargs):
        # checkout_data = request.data
        # gateway = checkout_data.get("gateway")
        # response = gateway.checkout()
        pk = int(kwargs.get("pk"))
        delivery_type = kwargs.get("delivery_type")
        delivery_type = DeliveryType.objects.filter(type=delivery_type)[0]
        if pk > 0:
            try:
                cart = Cart.objects.filter(pk=pk).first()

            except:
                logger.error("Accessing empty cart")
        else:
            cart = 0
        if cart or request.user:
            try:
                with transaction.atomic():
                    stock_verification = verify_stocks(cart, request.user.inventory)
                    if len(stock_verification) > 0:
                        return Response(
                            {
                                "message": "Stocks are not present for you order",
                                "out_of_stock": stock_verification,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if pk > 0:
                        try:
                            order = Order.objects.create(
                                customer=request.user,
                                cart=cart,
                                inventory=request.user.inventory,
                            )
                        except:
                            return Response(
                                {"message": "Error while creating order"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                        # getting all orderlist as string here
                        ordercontent = cart.get_order_list()
                        order.orderlist = ordercontent
                        # order.save()
                        # Total price get
                        order.delivery_charge = get_delivery_charge()
                        totalprice = cart.get_total_price()
                        order.total_price = (
                            totalprice
                            + Decimal.from_float(order.delivery_charge)
                            + Decimal.from_float(order.packaging_charge)
                        )

                        # getting the extra address field using serializer
                        content = OrderSerializer(data=request.data)
                        if content.is_valid():
                            order.save()

                    customer = order.customer
                    if (
                        DISCOUNT_SETTINGS.get(
                            "discount_promotional_enabled", ""
                        ).lower()
                        == "true"
                    ):
                        customer_promotional_discounts = (
                            customer.discountattributes_set.filter(
                                applied_on=CUSTOMER,
                                one_time_per_user=True,
                                attribute_type="promotional",
                            )
                        )
                        unused_discount_code = customer_promotional_discounts.filter(
                            discount__is_applied=False
                        ).exists()
                        if (
                            customer_promotional_discounts.count()
                            < int(DISCOUNT_SETTINGS.get("maximum_count", 0))
                            and not unused_discount_code
                        ):
                            discount_obj = create_promotional_discount(order, {})

                    order.checkout_address = "address"
                    order.delivery_type = delivery_type.type
                    order.source = WEBSITE
                    order.payment_status = CHECKOUT
                    order.status = PAYMENT_PENDING
                    order.save()

                    # Creating Payment for Order
                    payment = PaymentModel.objects.create(order=order)
                    payment.amount = order.total_price
                    payment.status = PENDING
                    payment.source = WEBSITE
                    payment.save()

                    # import ipdb ; ipdb.set_trace()
                    # Wallet Payment
                    if request.data["mode_of_payment"] == WALLET:
                        # Updating Payment Details
                        payment.mode = WALLET
                        payment.save()

                        # Updating Order Details
                        order.mode_of_payment = WALLET
                        order.save()

                        return Response(
                            {
                                "status": status.HTTP_201_CREATED,
                                "order_id": order.id,
                                "message": "Order is created!",
                                "order_amount": order.total_price,
                                "customer_name": customer.username,
                                "mode_of_payment": WALLET,
                            },
                            status=status.HTTP_201_CREATED,
                        )

                    # Online Payment
                    if (
                        request.data["mode_of_payment"] == ONLINE
                        and get_payment_mode(order.id) == RAZORPAY
                    ):
                        # Updating Payment Details
                        payment.gateway_type = RAZORPAY
                        payment.save()

                        client = razorpay.Client(
                            auth=(
                                settings.RAZORPAY_API_KEY,
                                settings.RAZORPAY_API_SECRET_KEY,
                            )
                        )
                        data = {
                            "amount": int(order.total_price * 100),
                            "currency": "INR",
                            "notes": {"order_id": order.id},
                        }
                        client_order = client.order.create(data=data)

                        return Response(
                            {
                                "status": status.HTTP_201_CREATED,
                                "order_id": order.id,
                                "email": customer.email,
                                "phone_no": customer.phone_number,
                                "message": "Order is created!",
                                "razorpay_order_id": client_order["id"],
                                "order_amount": order.total_price,
                                "customer_name": customer.username,
                                "RAZORPAY_API_KEY": settings.RAZORPAY_API_KEY,
                                "mode_of_payment": get_payment_mode(order.id),
                            },
                            status=status.HTTP_201_CREATED,
                        )

                    # Online Payment
                    if (
                        request.data["mode_of_payment"] == ONLINE
                        and get_payment_mode(order.id) == PAYTM
                    ):
                        # Updating Payment Details
                        payment.gateway_type = PAYTM
                        payment.save()
                        client = create_payment_order(
                            order.total_price, order.id, customer.phone_number
                        )
                        token = False
                        if "body" in client and "txnToken" in client["body"]:
                            token = client["body"]["txnToken"]

                        return Response(
                            {
                                "status": status.HTTP_201_CREATED,
                                "payment_detail": {
                                    "order_id": order.id,
                                    "amount": str(order.total_price),
                                    "token": token,
                                    "mid": settings.PAYTM_MERCHANT_ID,
                                    "website": settings.PAYTM_WEBSITE,
                                },
                                "mode_of_payment": get_payment_mode(order.id),
                                "message": "Order is created!",
                            },
                            status=status.HTTP_201_CREATED,
                        )

                    if request.data[
                        "mode_of_payment"
                    ] == ONLINE and not get_payment_mode(order.id):
                        return Response(
                            {
                                "status": status.HTTP_400_BAD_REQUEST,
                                "mode_of_payment": ONLINE,
                                "message": "Online payment is blocked for now!",
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Cash on Delivery
                    if request.data["mode_of_payment"] == COD:
                        # Updating Payment Details
                        payment.mode = CASH
                        payment.save()

                        # Updating Order Details
                        order.mode_of_payment = CASH
                        order.payment_status = PENDING
                        order.status = ORDER_PLACED
                        order.save()

                        # try:
                        #     update_inventory(order)
                        # except Exception as e:
                        #     logger.error(e)

                        # Updating Cart Details
                        cart.cartitem.all().update(is_active=False)
                        cart.status = ORDER_PLACED
                        cart.save()

                        # Send OTP
                        # try:
                        #     # VoiceOTPsend(settings.VOICE_PHONES)
                        #     # OTPsend(settings.PHONES)
                        #     #Sending notification to storemanager and admins for new order
                        #     users = Profile.objects.filter(Q(inventory=request.user.inventory, role="SK") | Q(role="ADMIN"))
                        #     device_ids = []
                        #     for user in users:
                        #         device_ids.append(user.device_id)
                        #     message_title = "New Order"
                        #     message_body = "You have a new order"
                        #     extra_notification_kwargs = {
                        #             'sound': 'notification.wav',
                        #             "android_channel_id": "hello"}
                        #     result = push_service.notify_multiple_devices(registration_ids=device_ids, message_title=message_title, message_body=message_body, extra_notification_kwargs=extra_notification_kwargs)

                        # except Exception as err:
                        #         logger.error(str(err))

                        # send order communication
                        # if settings.MESSAGE_SEND:
                        #     send_order_communication(order,payment)

                        return Response(
                            {
                                "status": status.HTTP_201_CREATED,
                                "order_id": order.id,
                                "mode_of_payment": COD,
                                "message": "Order is placed!",
                            },
                            status=status.HTTP_201_CREATED,
                        )

                    return Response(
                        {
                            "message": "Order Failed",
                        }
                    )
            except Exception as e:
                logger.error(str(e))
                return Response(
                    {"msg": str(e), "status": status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "message": "Order is not placed",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    @action(methods=["POST"], detail=False)
    def success(self, request, *args, **kwargs):
        success_data = request.data
        gateway_name = success_data.get("gateway")  # razorpay # paytm
        gateway_name = (
            "".join(gateway_name.split("-"))
            if len(gateway_name.split("-")) > 1
            else gateway_name
        )
        gateway_class_name = "%sGateway" % gateway_name.upper()
        gateway_class = getattr(gateways, gateway_class_name, gateways.BaseGateway)
        gateway = gateway_class()
        response = gateway.success(request)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=["POST"], detail=False)
    def failure(self, request, *args, **kwargs):
        failure_data = request.data
        gateway_name = failure_data.get("gateway")  # razorpay
        gateway_name = (
            "".join(gateway_name.split("-"))
            if len(gateway_name.split("-")) > 1
            else gateway_name
        )
        gateway_class_name = "%sGateway" % gateway_name.upper()
        gateway_class = getattr(gateways, gateway_class_name, gateways.BaseGateway)
        gateway = gateway_class()
        response = gateway.failure(request)
        return Response(status=status.HTTP_201_CREATED)
