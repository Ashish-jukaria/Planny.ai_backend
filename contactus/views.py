from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.conf import settings
import http.client
import json


def OTPsend(PHONE):
    TOKEN = settings.API_KEY_2FACTOR
    conn = http.client.HTTPConnection("2factor.in")
    payload = ""
    headers = {"content-type": "application/x-www-form-urlencoded"}
    for j in PHONE:
        conn.request(
            "GET", f"/API/V1/{TOKEN}/SMS/{j}/Phuti/Send%20OTP", payload, headers
        )
        res = conn.getresponse()
        data = res.read()
        response = {
            "status": status.HTTP_200_OK,
            "data": json.loads(data.decode("utf-8")),
        }
        print(response)


@api_view(["GET"])
def get_item_list(request, *args, **kwargs):
    data = Items.objects.all()
    serializer = ItemsSerializer(data, many=True)
    if data:
        return Response(
            {
                "data": serializer.data,
                "status": status.HTTP_200_OK,
                "message": "Order items are fetched!",
            }
        )
    else:
        return Response(
            {
                "data": [],
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Order items are empty!",
            }
        )
