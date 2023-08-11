from account.models import *
from django.conf import settings


def send_promotional_sms(phone):
    import requests
    import json

    TOKEN = settings.API_KEY_2FACTOR
    url = f"http://2factor.in/API/V1/{TOKEN}/ADDON_SERVICES/SEND/PSMS"
    code = "MONDAY50"
    msg = f"Groceries Delivered in 10 Minutes. Get Flat 50% Discount on your first oder. Visit www.Phurti.in and use Code {code}."
    payload = {"From": "PHURTI", "To": phone, "Msg": msg}
    files = []
    headers = {"Content-Type": "application/json; charset=utf-8"}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print(response)
    print("JSON Response ", response.json())
    print("Status Code", response.status_code)


def send_promotional_sms_to_all_users():
    users = Profile.objects.all()
    for user in users:
        phone = user.phone_number
        if not user.is_superuser:
            print(phone)
            send_promotional_sms(phone)
