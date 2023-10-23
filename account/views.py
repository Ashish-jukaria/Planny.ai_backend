import logging
import json
from rest_framework import viewsets
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from notifications.views import send_order_communication
from phurti.settings import MESSAGE_SEND
from shop.views import update_inventory
from shop.constants import *
from phurti.constants import *
from account.models import Profile, TenantUser, Feedback, Wallet
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework import generics
from pyfcm import FCMNotification
from shop.models import (
    Order,
    Payment,
    Cart,
)
from account.utils import *
from rest_framework.decorators import action
from account.utils import *
from payments.api.views import get_payment_mode
from payments.gateways.paytm.utils import create_payment_order, transaction_detail
from payments.constants import PAYTM
from payments.gateways.paytm.views import payment_code

push_service = FCMNotification(api_key=settings.FCM_API_KEY)

logger = logging.getLogger("phurti")


@api_view(["POST"])
def sendOTP(request, **kwargs):
    PHONE = kwargs.get("phone")
    response = {
        "status": status.HTTP_200_OK,
        "data": {
            "Status": "Success",
            "Details": "l60gaseavbemjvlgw7o-7303503698702e11",
            "OTP": "565059",
        },
    }
    return Response(response, status=response["status"])


@api_view(["GET", "POST"])
def verifyOTP(request, **kwargs):
    if request.method == "GET":
        PHONE = kwargs.get("phone")
        #  SESSION_ID = kwargs.get("session_id")
        OTP = kwargs.get("otp")
        response = {"data": {"Details": "OTP Matched"}}
        if response["data"]["Details"] == "OTP Matched":
            Profile.objects.filter(phone_number=PHONE).update(is_verified=True)
            user = Profile.objects.filter(phone_number=PHONE).first()
            serializer = UserProfileSerializer(user, many=False)
            data = get_tokens_for_user(PHONE)
            response["token"] = data
            response["user"] = serializer.data
            response["data"]["code"] = status.HTTP_200_OK

        else:
            response["data"]["code"] = status.HTTP_400_BAD_REQUEST
        return Response(response, status=response["data"]["code"])

    elif request.method == "POST":
        PHONE = kwargs.get("phone")
        # SESSION_ID = kwargs.get("session_id")
        OTP = kwargs.get("otp")
        response = OTPverify(PHONE, SESSION_ID, OTP)
        if response["data"]["Details"] == "OTP Matched":
            # import ipdb
            # ipdb.set_trace()
            Profile.objects.filter(phone_number=PHONE).update(is_verified=True)
            Profile.objects.filter(phone_number=PHONE).update(
                device_id=request.data.get("device_id")
            )
            user = Profile.objects.filter(phone_number=PHONE).first()
            serializer = UserProfileSerializer(user, many=False)
            data = get_tokens_for_user(PHONE)
            response["token"] = data
            response["user"] = serializer.data
            response["data"]["code"] = status.HTTP_200_OK

        else:
            response["data"]["code"] = status.HTTP_400_BAD_REQUEST
        return Response(response, status=response["data"]["code"])


class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        serializer = Registration(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response["data"] = serializer.data
            response["status"] = status.HTTP_201_CREATED
            response["msg"] = "Register successfully!"
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    "data": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = Profile.objects.filter(phone_number=serializer.data["phone_number"])

            if user:
                user_verified = user.filter(is_verified=True)
                if user_verified:
                    password = user.first().check_password(serializer.data["password"])
                    if password:
                        token = get_tokens_for_user(serializer.data["phone_number"])
                        response["token"] = token
                        response["status"] = status.HTTP_200_OK
                        response["msg"] = "Login successfully!"
                        return Response(response, status=status.HTTP_200_OK)
                    else:
                        response["status"] = status.HTTP_400_BAD_REQUEST
                        response["msg"] = "Password is wrong"
                        return Response(response, status=status.HTTP_400_BAD_REQUEST)

                else:
                    response["status"] = status.HTTP_400_BAD_REQUEST
                    response["msg"] = "User not verified"
                    response["is_verified"] = "false"
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            else:
                response["status"] = status.HTTP_400_BAD_REQUEST
                response["msg"] = "User not found."
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {
                    "data": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            )


# import ipdb
# ipdb.set_trace()


class AlternativeUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # get_user(request) # getting user from token
        response = {}
        if request.data:
            addresses = request.user.attributes["ADDRESSES"]
            last_id = addresses[-1]["id"] + 1
            request.data["id"] = last_id
            addresses.append(request.data)
            request.user.attributes["ADDRESSES"] = addresses
            request.user.save()
            response["status"] = status.HTTP_201_CREATED
            response["msg"] = "Added Success!"
        return Response(response, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        # get_user(request) # getting user from token
        response = {}
        user_default_address = request.user.attributes["ADDRESSES"][-1]
        response["data"] = [user_default_address]
        response["status"] = status.HTTP_200_OK
        response["msg"] = "Success!"
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        # get_user(request) # getting user from token
        response = {}
        addresses = request.user.attributes["ADDRESSES"]
        address_ids = [
            i
            for i, address in enumerate(addresses)
            if address["id"] == request.data["id"]
        ]
        if len(address_ids):
            addresses[address_ids[-1]].update(request.data)
            request.user.attributes["ADDRESSES"] = addresses
            request.user.save()
            response["status"] = status.HTTP_201_CREATED
            response["msg"] = "Success!"
            return Response(response)
        else:
            return Response(
                {
                    "data": "No address found!",
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            )


@api_view(["POST"])
def feedback(request, **kwargs):
    data = FeedbackSerializer(data=request.data)
    if data.is_valid():
        order = data.data["order_id"]
        order_detail = Order.objects.filter(pk=order)

        feedback_form = Feedback.objects.create(
            order_id=order_detail.first(),
            rating=data.data["rating"],
            comments=data.data["comments"],
        )

        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "message": "Thanks for your feedback!",
            }
        )
    else:
        return Response(
            {
                "data": data.errors,
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Something went wrong!",
            }
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        response = {}
        user = Profile.objects.filter(
            pk=request.user.id, tenant=request.tenant_id
        ).first()
        serializer = UserProfileSerializer(user, many=False)
        response["data"] = serializer.data
        response["status"] = status.HTTP_200_OK
        response["msg"] = "Success"

        return Response(response, status=response["status"])


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = {}
        wallet = Wallet.objects.filter(user=request.user).first()
        if wallet:
            serializer = WalletSerializer(wallet, many=False)
            response["data"] = serializer.data
            response["status"] = status.HTTP_200_OK
            response["msg"] = "Success"
        else:
            response["data"] = []
            response["status"] = status.HTTP_400_BAD_REQUEST
            response["message"] = "No wallet found."

        return Response(response, status=response["status"])

    def post(self, request):
        response = {}
        order_id = request.data["order_id"]
        serializer = WalletMiniSerializer(data=request.data)
        try:
            with transaction.atomic():
                if serializer.is_valid():
                    wallet = Wallet.objects.filter(user=request.user).first()

                    amount = Decimal(serializer.data["amount"])
                    transaction_type = serializer.data["transaction_type"]
                    wallet_transaction_obj = wallet.update_wallet_balance(
                        transaction_type, amount
                    )
                    payment_status = FAILED
                    transaction_id = None

                    if type(wallet_transaction_obj) == WalletTransaction:
                        if wallet_transaction_obj.status == SUCCESS:
                            payment_status = SUCCESS
                        transaction_id = wallet_transaction_obj.transaction_id

                    # Updating Order Details
                    order_id = serializer.data["order_id"]
                    order = Order.objects.filter(pk=order_id).first()
                    order.payment_status = payment_status

                    # Updating payment Details
                    payment = Payment.objects.filter(order=order).first()
                    payment.status = payment_status
                    payment.payment_date = str(timezone.now())
                    payment.txn_id = transaction_id

                    # Linking Order to Payment
                    payment.order = order

                    # Saving Order and Payment
                    order.save()
                    payment.save()

                    if payment_status == SUCCESS:
                        # Send OTP if Payment successful
                        try:
                            # VoiceOTPsend(settings.VOICE_PHONES)
                            # OTPsend(settings.PHONES)
                            # Sending notification to storemanager and admins for new order
                            users = Profile.objects.filter(
                                Q(inventory=request.user.inventory, role="SK")
                                | Q(role="ADMIN")
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

                        # Update inventory
                        try:
                            update_inventory(order)
                        except Exception as e:
                            logger.error(e)

                        # Updating Cart Details
                        cart = Cart.objects.filter(customer=order.customer).last()
                        cart.cartitem.all().update(is_active=False)
                        cart.status = ORDER_PLACED
                        cart.save()

                        # Send Order Confirmation message
                        if settings.MESSAGE_SEND:
                            send_order_communication(order, payment)

                    response["data"] = {
                        "txn": transaction_id,
                        "payment_id": payment.id,
                        "wallet_balance": wallet.balance,
                    }
                    response["status"] = status.HTTP_200_OK
                    response["message"] = "Success"
                    return Response(response, status=response["status"])
                else:
                    return Response(
                        {
                            "data": serializer.errors,
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Something went wrong!",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except Exception as e:
            logger.log(str(e))
            return Response(
                {
                    "data": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Transaction failed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = Profile.objects.all()


# TENANTVIEW for read, update, and delete data
class TenantView(APIView):
    def get(self, request, id):
        obj = Tenant.objects.filter(id=id)
        if not obj:
            return Response({"No Such Record with id ": id})
        obj = obj[0]
        serializer = TenantSerializer(obj)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        serializer = TenantSerializer(data=data)
        if serializer.is_valid():
            tenant = serializer.save()
            tenant.admins.add(request.user.id)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def put(self, request, id):
        data = request.data
        obj = Tenant.objects.filter(id=id)
        if obj:
            obj = obj[0]
        else:
            return Response({"No Such Record with id ": id})
        serializer = TenantSerializer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, id):
        obj = Tenant.objects.filter(id=id)
        if obj:
            obj = obj[0]
        else:
            return Response({"No Such Record with id ": id})
        obj.delete()
        return Response({"deleted"})


class TenantUserList(APIView):
    def post(self, request, format=None):
        serializer = TenantUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantUserDetail(APIView):
    def get_object(self, pk):
        try:
            return TenantUser.objects.get(pk=pk)
        except TenantUser.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = TenantUserDetailSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = TenantUserDetailSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TenanteUserRegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = TenantUser.objects.all()
    serializer_class = TenantRegisterSerializer


def get_tokens_for_tenant_user(phone):
    user = TenantUser.objects.filter(phone_number=phone).first()
    if user:
        payload = {
            "user_type": "tenant",
            "user_id": user.id,
            "phone_number": user.phone_number,
        }
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token.payload.update(payload)

        return {
            "refresh": str(refresh),
            "access": str(access_token),
        }
    else:
        return {"details": "User not found"}


@api_view(["POST"])
def tenant_user_send_otp(request, **kwargs):
    PHONE = request.GET.get("phone")
    response = {
        "status": status.HTTP_200_OK,
        "data": {
            "Status": "Success",
            "Details": "l60gaseavbemjvlgw7o-7303503698702e11",
            "OTP": "565059",
        },
    }
    return Response(response, status=response["status"])


@api_view(["POST"])
def tenant_user_verify_otp(request, **kwargs):
    if request.method == "POST":
        PHONE = request.data.get("phone")
        SESSION_ID = request.data.get("session_id")
        OTP = request.data.get("otp")
        response = {"data": {"Details": "OTP Matched"}}
        if response["data"]["Details"] == "OTP Matched":
            TenantUser.objects.filter(phone_number=PHONE).update(is_verified=True)
            user = TenantUser.objects.filter(phone_number=PHONE).first()
            serializer = TenantUserSerializer(user, many=False)
            data = get_tokens_for_tenant_user(PHONE)
            response["token"] = data
            response["user"] = serializer.data
            response["data"]["code"] = status.HTTP_200_OK

        else:
            response["data"]["code"] = status.HTTP_400_BAD_REQUEST
        return Response(response, status=response["data"]["code"])


class SubscriptionView(APIView):
    def get(self, request):
        response = {}
        if request.method == "GET":
            subscription = Subscription.objects.filter(is_active=True)
            serializer = SubscriptionSerializer(subscription, many=True)
            response["data"] = serializer.data
            response["status"] = status.HTTP_200_OK
            response["msg"] = "Success"

            return Response(response, status=response["status"])


class SubscriptionDetailView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        response = {}
        today = datetime.now()
        tenant = Tenant.objects.get(id=request.tenant_id)
        admin = tenant.admins.values_list("phone_number", flat=True)
        if request.user.phone_number in admin:
            subscription = SubscriptionDetail.objects.filter(
                tenant_id=request.tenant_id, end_date__gte=today
            ).first()
            serializer = SubscriptionDetailSerializer(subscription)
            response["data"] = serializer.data
            response["status"] = status.HTTP_200_OK
            response["msg"] = "Success"
            return Response(response, status=response["status"])
        else:
            response["status"] = status.HTTP_200_OK
            response["msg"] = "User Not Found"
            return Response(response, status=response["status"])


class TenantCategoryList(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        snippet = TenantCategory.objects.all()
        serializer = TenantCategorySerializer(snippet, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ViewSet):
    """
    Payment method to create subscription and save payment details.
    """

    permission_classes = [IsAuthenticated]

    def create_subscription_detail(self, payment, subscription_id, tenant_id):
        subscription_details = Subscription.objects.filter(pk=subscription_id).first()
        subscription_detail_data = {
            "tenant_id_id": tenant_id,
            "subscription_id": subscription_details,
            "end_date": subscription_details.calculate_expiry_date(),
            "status": "A",
        }
        subscription_detail_serializer = SubscriptionDetailSerializer(
            data=subscription_detail_data
        )
        subscription_detail_serializer.is_valid(raise_exception=True)
        subscription_detail_serializer.save()
        return subscription_detail_serializer

    @action(detail=False, methods=["post"])
    def initiate(self, request):
        subscription_id = request.query_params.get("subscription_id")
        subscription = Subscription.objects.filter(id=subscription_id)
        if not subscription.exists():
            return Response(
                {"success": False, "message": "Subscription not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Creating Payment for Subscription
        payment = Payment.objects.create(amount=subscription.price)
        payment.status = PENDING
        payment.source = WEBSITE
        payment.save()

        if get_payment_mode(subscription.id) == PAYTM:
            payment.gateway_type = PAYTM
            payment.save()
            client = create_payment_order(
                subscription.price, subscription_id, request.user.phone_number
            )
            token = False
            if "body" in client and "txnToken" in client["body"]:
                token = client["body"]["txnToken"]

            user_subscription_details = self.create_subscription_detail(
                payment, subscription_id, request.tenant_id
            )
        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "payment_detail": {
                    "user_subscription_id": user_subscription_details.id,
                    "amount": str(subscription.price),
                    "token": token,
                    "mid": settings.PAYTM_MERCHANT_ID,
                    "website": settings.PAYTM_WEBSITE,
                },
                "mode_of_payment": get_payment_mode(subscription_id),
                "message": "Subscription is added!",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def success(self, request):
        user_subscription_id = request.POST.get("user_subscription_id")
        data = request.data
        payment = SubscriptionDetail.objects.get(pk=user_subscription_id).payment

        transaction_details = transaction_detail(user_subscription_id)
        # Updating Payment Details"
        payment.status = SUCCESS
        payment.payment_id = data["TXNID"]
        payment.payment_date = str(timezone.now())
        payment.mode = payment_code[data["PAYMENTMODE"]]
        payment.additional_details = json.dumps(transaction_details["body"])
        payment.save()
        return Response({"success": True})

    @action(detail=False, methods=["post"])
    def failure(self, request):
        user_subscription_id = request.POST.get("user_subscription_id")
        data = request.data

        transaction_details = transaction_detail(order_id)
        payment = SubscriptionDetail.objects.get(pk=user_subscription_id).payment

        # Updating Payment Details
        payment.status = FAILED
        payment.payment_id = data["TXNID"]
        payment.mode = payment_code[data["PAYMENTMODE"]]
        payment.payment_date = str(timezone.now())
        payment.additional_details = json.dumps(transaction_details["body"])
        payment.save()
        return Response({"success": True})


class UserAllTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenants = Tenant.objects.filter(
            admins__phone_number=request.user.phone_number
        )  # bring add tenant that has user phonenumber
        serializer = TenantSerializer(tenants, many=True)
        response_dict = {
            "status": "success",
            "data": serializer.data,
        }
        return Response(response_dict)


class TenantSearchAPI(generics.ListAPIView):
    queryset = Tenant.objects.none()  # Empty initial queryset
    serializer_class = TenantSerializer

    def get_queryset(self):
        search_query = self.request.query_params.get('q')

        if search_query:
            queryset = Tenant.objects.filter(title__icontains=search_query)
            return queryset

        return self.queryset  # Return empty queryset if no search query provided