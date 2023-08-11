from shop.models import *
import json
import os
import datetime


def put_detail():
    get_model_data = Order.objects.all()
    dump_data = []
    with open("order_data.txt", "r") as data:
        dump_data = json.loads(data.read())

    for j in range(len(dump_data)):
        if get_model_data[j].id == dump_data[j][0]:
            Order.objects.filter(pk=get_model_data[j].id).update(
                created=dump_data[j][1]
            )
            Order.objects.filter(pk=get_model_data[j].id).update(
                updated=dump_data[j][2]
            )


def create_cache(dump_data, date):
    fname = "orderscheduler_data/scheduler.json"
    schedule_data = {}

    if not os.path.isfile(fname):
        schedule_data[date] = []
        schedule_data[date].append(dump_data)

        with open(fname, mode="w") as f:
            f.write(json.dumps(schedule_data, indent=2))
    else:
        with open(fname) as task:
            feeds = json.load(task)

        if date not in feeds:
            feeds[date] = [dump_data]
        else:
            feeds[date].append(dump_data)
        with open(fname, mode="w") as f:
            f.write(json.dumps(feeds, indent=2))


def get_user(request):
    from rest_framework_simplejwt.backends import TokenBackend

    # token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQwNTAzNDkzLCJqdGkiOiIzNGRmN2Y1ZDY5OTc0MzEyOTExMjAxOGU3ZWY2MGE5NyIsInVzZXJfaWQiOjJ9.-_q951MA0Axe1wRkJlmXOqCRwmNhdYP9ovO3E0MkKp8"
    data = {"token": token}
    valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
    user = valid_data["user_id"]
    request.user = Customer.objects.filter(pk=user).first()
    print(request.user)
