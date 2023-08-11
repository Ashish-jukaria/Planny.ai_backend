import http.client
import random
import json
import account.models
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


def generate_wallet_transaction_id(generator):
    return f"wtxn_{generator:010}"


def generateOTP():
    OTP = str(random.randint(1000, 9999))
    return OTP


def get_tokens_for_user(phone):
    user = account.models.Profile.objects.filter(phone_number=phone).first()
    if user:
        payload = {
            "user_type": "profile",
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


def OTPsend(PHONE):
    TOKEN = settings.API_KEY_2FACTOR
    # PHONE = kwargs.get("PHONE")
    user_check = account.models.Profile.objects.filter(phone_number=PHONE).exists()
    if user_check:
        # OTP = generateOTP()
        conn = http.client.HTTPConnection("2factor.in")
        payload = ""
        headers = {"content-type": "application/x-www-form-urlencoded"}
        conn.request(
            "GET",
            f"/API/V1/{TOKEN}/SMS/{PHONE}/AUTOGEN/Send%20OTP",
            payload,
            headers,
        )
        res = conn.getresponse()
        data = res.read()
        response = {
            "status": status.HTTP_200_OK,
            "data": json.loads(data.decode("utf-8")),
        }
    else:
        response = {
            "status": status.HTTP_404_NOT_FOUND,
            "msg": "User Not Found",
        }

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
        "GET",
        f"/API/V1/{TOKEN}/SMS/VERIFY/{SESSION_ID}/{OTP}",
        payload,
        headers,
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


def tenant_user_otp_send(PHONE):
    TOKEN = settings.API_KEY_2FACTOR
    # PHONE = kwargs.get("PHONE")
    user_check = account.models.TenantUser.objects.filter(phone_number=PHONE).exists()
    if user_check:
        # OTP = generateOTP()
        conn = http.client.HTTPConnection("2factor.in")
        payload = ""
        headers = {"content-type": "application/x-www-form-urlencoded"}
        conn.request(
            "GET",
            f"/API/V1/{TOKEN}/SMS/{PHONE}/AUTOGEN/Send%20OTP",
            payload,
            headers,
        )
        res = conn.getresponse()
        data = res.read()
        response = {
            "status": status.HTTP_200_OK,
            "data": json.loads(data.decode("utf-8")),
        }
    else:
        response = {
            "status": status.HTTP_404_NOT_FOUND,
            "msg": "User Not Found",
        }

    return response


def CheckTenant(request):
    """
    Function to filter out tenant from request body or from query paramter(if it's not in request body).
    """
    data = request.data
    tenant_request_body = data.get("tenant", "")
    tenant_query_parameter = request.GET.get("tenant", "")
    has_tenant = tenant_request_body or tenant_query_parameter

    if not has_tenant:
        return False
    tenant = account.models.Tenant.objects.filter(id=has_tenant).first()
    if not tenant:
        return False
    else:
        return tenant
