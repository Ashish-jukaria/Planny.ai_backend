from django.shortcuts import render
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from shop.models import *
from shop.serializers import *
from account import models as account_models
from shop.constants import *
from rest_framework.response import Response
from pyfcm import FCMNotification
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from shop.paginations import *
from django.conf import settings
from phurti.constants import *
from rest_framework import status
import logging
from django.db.models import Q

logger = logging.getLogger("phurti")
push_service = FCMNotification(api_key=settings.FCM_API_KEY)
from datetime import datetime
from .utils import *


@api_view(["GET"])
def fetch_executives(request, inventory):
    try:
        response = {}

        executives_temp = account_models.Profile.objects.filter(
            Q(role="DP") | Q(role="SK"), inventory_id=inventory
        )
        serializer = ProfileSerializer(executives_temp, many=True)
        if serializer.data:
            response["executives"] = serializer.data
            response["status"] = status.HTTP_200_OK
            return Response(response)
        else:
            response["status"] = status.HTTP_400_BAD_REQUEST
            return Response(response)
    except Exception as err:
        logger.error(str(err))
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assignOrders(request):
    try:
        order = Order.objects.filter(id=request.data["order_id"])
        order.update(delivered_by=request.data["delivery_id"])
        order.update(status="ASSIGNED")
        device_id = Profile.objects.get(id=request.data["delivery_id"]).device_id
        message_title = "New Order"
        message_body = "You have a new order"
        extra_notification_kwargs = {
            "sound": "notification.wav",
            "android_channel_id": "hello",
        }
        result = push_service.notify_single_device(
            registration_id=device_id,
            message_title=message_title,
            extra_notification_kwargs=extra_notification_kwargs,
            message_body=message_body,
        )
        return Response({"status": status.HTTP_200_OK})
    except Exception as err:
        logger.error(str(err))
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order(request):
    try:
        order = Order.objects.filter(id=request.data["order_id"])
        order.update(status=request.data["status"])

        if request.data["status"] == "DELIVERED":
            order.update(delivered=True)

        if request.data["dateAndTime"] != "":
            dateTimeObject = miliSecondToDateTime(int(request.data["dateAndTime"]))
            order.update(delivery_time=dateTimeObject)
        else:
            order.update(delivery_time=datetime.now())
        if order:
            return Response({"status": status.HTTP_200_OK})

        else:
            return Response({"status": status.HTTP_400_BAD_REQUEST})
    except Exception as err:
        logger.error(str(err))
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_payment_mode(request):
    try:
        order = Order.objects.filter(id=request.data["order_id"])
        order.update(mode_of_payment=request.data["mode_of_payment"])
        order.update(payment_status="SUCCESS")
        if order:
            return Response({"status": SUCCESS})
        else:
            return Response({"status": FAILED})
    except Exception as err:
        logger.error(str(err))
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def get_user_details(request, id):
    try:
        response = {}
        user = Profile.objects.get(id=id)
        serializer = CustomerSerializer(user)
        if serializer.data:
            response["user"] = serializer.data
            response["status"] = SUCCESS
            return Response(response)
        else:
            response["status"] = FAILED
            return Response(response)
    except Exception as err:
        logger.error(str(err))
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class fetch_orders(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    response = {}
    queryset = Order.objects.all().order_by("-created_on")
    serializer_class = RecentOrderSerializer
    pagination_class = OrderListPagination

    def get_queryset(self):
        try:
            order = {}
            if self.request.user.role == "DP":
                if self.kwargs["status"] == "ASSIGNED":
                    order = Order.objects.filter(
                        Q(status=self.kwargs["status"]) | Q(status="IN_PACKAGING"),
                        delivered_by=self.request.user.id,
                        inventory=self.request.user.inventory,
                    ).order_by("-created_on")
                else:
                    order = Order.objects.filter(
                        status=self.kwargs["status"],
                        delivered_by=self.request.user.id,
                        inventory=self.request.user.inventory,
                    ).order_by("-created_on")

            elif self.request.user.role == "ADMIN":
                if self.kwargs["status"] == "ORDER_PLACED":
                    order = (
                        Order.objects.filter(status=self.kwargs["status"])
                        .exclude(source__isnull=True)
                        .filter(~Q(source=PAYMENT_SOURCES[2][1]))
                        .order_by("-created_on")
                    )
                elif self.kwargs["status"] == "IN_PACKAGING":
                    order = (
                        Order.objects.filter(
                            Q(status=self.kwargs["status"])
                            | Q(status="IN_TRANSIT")
                            | Q(status="ASSIGNED")
                        )
                        .filter(~Q(source=PAYMENT_SOURCES[2][1]))
                        .order_by("-created_on")
                    )
                elif self.kwargs["status"] == "DELIVERED":
                    order = (
                        Order.objects.filter(status=self.kwargs["status"])
                        .exclude(source=PAYMENT_SOURCES[2][1])
                        .order_by("-created_on")
                    )
                elif self.kwargs["status"] == "EVERYTHING":
                    order = Order.objects.filter(source=PAYMENT_SOURCES[2][1]).order_by(
                        "-created_on"
                    )
            elif self.kwargs["status"] == "ORDER_PLACED":
                order = (
                    Order.objects.filter(
                        inventory=self.request.user.inventory,
                        status=self.kwargs["status"],
                    )
                    .exclude(source__isnull=True)
                    .filter(~Q(source=PAYMENT_SOURCES[2][1]))
                    .order_by("-created_on")
                )
            elif self.kwargs["status"] == "IN_PACKAGING":
                order = Order.objects.filter(
                    Q(status=self.kwargs["status"])
                    | Q(status="IN_TRANSIT")
                    | Q(status="ASSIGNED"),
                    inventory=self.request.user.inventory,
                ).order_by("-created_on")
            elif self.kwargs["status"] == "EVERYTHING":
                order = Order.objects.filter(
                    source=PAYMENT_SOURCES[2][1], inventory=self.request.user.inventory
                ).order_by("-created_on")
            elif self.kwargs["status"] == "DELIVERED":
                order = (
                    Order.objects.filter(
                        inventory=self.request.user.inventory,
                        status=self.kwargs["status"],
                    )
                    .exclude(source=PAYMENT_SOURCES[2][1])
                    .order_by("-created_on")
                )
            if (
                order.first().id > self.kwargs["offset"]
                or order.first().id < self.kwargs["offset"]
            ):
                return order
            else:
                return []
        except Exception as err:
            logger.error(str(err))
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Something went wrong.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
def logout_user(request):
    try:
        Profile.objects.filter(id=request.user.id).update(device_id="")
        return Response({"status": status.HTTP_200_OK})
    except Exception as err:
        logger.error(str(err))
        return Response(
            {"status": status.HTTP_400_BAD_REQUEST, "message": "Something went wrong."},
            status=status.HTTP_400_BAD_REQUEST,
        )
