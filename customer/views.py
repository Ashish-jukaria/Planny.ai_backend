from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import http.client
import random
import json
from django.conf import settings
from shop.models import Order
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from scripts.put_detail import get_user


def generateOTP():
    OTP = str(random.randint(1000, 9999))
    return OTP


def get_tokens_for_user(phone):
    user = Customer.objects.filter(phone=phone)
    if user:
        refresh = RefreshToken.for_user(user.first())
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    else:
        return {"details": "User not found"}


def OTPsend(PHONE):
    TOKEN = settings.API_KEY_2FACTOR
    # PHONE = kwargs.get("PHONE")
    OTP = generateOTP()
    conn = http.client.HTTPConnection("2factor.in")
    payload = ""
    headers = {"content-type": "application/x-www-form-urlencoded"}
    conn.request(
        "GET", f"/API/V1/{TOKEN}/SMS/{PHONE}/AUTOGEN/Send%20OTP", payload, headers
    )
    res = conn.getresponse()
    data = res.read()
    response = {"status": status.HTTP_200_OK, "data": json.loads(data.decode("utf-8"))}

    return response


def OTPverify(PHONE, SESSION_ID, OTP):
    TOKEN = settings.API_KEY_2FACTOR
    # PHONE = kwargs.get("PHONE")
    # SESSION_ID = kwargs.get("SESSION_ID")
    # OTP = kwargs.get("OTP")
    conn = http.client.HTTPConnection("2factor.in")
    payload = ""
    headers = {"content-type": "application/x-www-form-urlencoded"}
    conn.request(
        "GET", f"/API/V1/{TOKEN}/SMS/VERIFY/{SESSION_ID}/{OTP}", payload, headers
    )
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)
    # {
    #     "data": {
    #         "Status": "Error", "Status": "Success", "Status": "Success",
    #         "Details": "OTP Mismatch", "Details": "OTP Matched", "Details": "OTP Expired"
    #     }
    # }
    response = {"data": data}

    return response


@api_view(["POST"])
def sendOTP(request, **kwargs):
    PHONE = kwargs.get("phone")
    response = OTPsend(PHONE)
    return Response(response)


@api_view(["GET"])
def verifyOTP(request, **kwargs):
    PHONE = kwargs.get("phone")
    SESSION_ID = kwargs.get("session_id")
    OTP = kwargs.get("otp")
    response = OTPverify(PHONE, SESSION_ID, OTP)
    if response["data"]["Details"] == "OTP Matched":
        Customer.objects.filter(phone=PHONE).update(is_verified=True)
        data = get_tokens_for_user(PHONE)
        response["token"] = data
        response["data"]["code"] = status.HTTP_200_OK

    else:
        response["data"]["code"] = status.HTTP_400_BAD_REQUEST
    return Response(response)


class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        serializer = Registration(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response["data"] = serializer.data
            response["status"] = status.HTTP_201_CREATED
            response["msg"] = "Register successfully!"
            return Response(response)
        else:
            return Response(
                {"data": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}
            )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = Customer.objects.filter(phone=serializer.data["phone"])

            if user:
                password = user.first().password_checker(serializer.data["password"])
                if password:
                    token = get_tokens_for_user(serializer.data["phone"])
                    response["token"] = token
                    response["status"] = status.HTTP_200_OK
                    response["msg"] = "Login successfully!"
                    return Response(response)
                else:
                    response["status"] = status.HTTP_400_BAD_REQUEST
                    response["msg"] = "Password is wrong"
                    return Response(response)
            else:
                response["status"] = status.HTTP_400_BAD_REQUEST
                response["msg"] = "User not found."
                return Response(response)

        else:
            return Response(
                {"data": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}
            )


# import ipdb
# ipdb.set_trace()


@api_view(["POST"])
def AlternativeUpdate(request, *args, **kwargs):
    if request.method == "POST":
        get_user(request)  # getting user from token
        response = {}
        serializer = AlternativeSerializer(data=request.data)
        if serializer.is_valid():
            Alternative.objects.create(
                customer=request.user,
                type=serializer.data["type"],
                value=serializer.data["value"],
            )
            response["data"] = serializer.data
            response["status"] = status.HTTP_201_CREATED
            response["msg"] = "Added Success!"
            return Response(response)
        else:
            return Response(
                {"data": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}
            )
