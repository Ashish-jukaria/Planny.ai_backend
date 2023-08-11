from shop.models import *
from account.models import *
import pandas as pd

cohort = {}


def hello():
    phones = []

    users = Profile.objects.filter(is_staff=0)

    for user in users:
        phones.append(user.phone_number)
        orders = Order.objects.filter(customer=user)
        user_obj = User.objects.filter(phone=user.phone_number).first()
        prev_orders = []
        rev = 0
        if user_obj:
            prev_orders = Order.objects.filter(user=user_obj)
        cohort[user.phone_number] = {}
        for i in range(28, 63):
            if i <= 52:
                cohort[user.phone_number][i] = {"count": 0, "rev": 0}
            else:
                cohort[user.phone_number][i % 52] = {"count": 0, "rev": 0}
        for order in orders:
            cohort[user.phone_number][int(order.created_on.date().strftime("%V"))][
                "count"
            ] += 1
            cohort[user.phone_number][int(order.created_on.date().strftime("%V"))][
                "rev"
            ] += (float(order.total_price) if order.total_price else 0)
        for prev_order in prev_orders:
            cohort[user.phone_number][int(prev_order.created_on.date().strftime("%V"))][
                "count"
            ] += 1
            cohort[user.phone_number][int(prev_order.created_on.date().strftime("%V"))][
                "rev"
            ] += (float(prev_order.total_price) if prev_order.total_price else 0)

    old_users = User.objects.all()
    for old_user in old_users:
        if old_user.phone in phones:
            pass
        else:
            orders = Order.objects.filter(user=old_user)
            cohort[old_user.phone] = {}
            for i in range(28, 63):
                if i <= 52:
                    cohort[old_user.phone][i] = {"count": 0, "rev": 0}
                else:
                    cohort[old_user.phone][i % 52] = {"count": 0, "rev": 0}
            for order in orders:
                cohort[old_user.phone][int(order.created_on.date().strftime("%V"))][
                    "count"
                ] += 1
                cohort[old_user.phone][int(order.created_on.date().strftime("%V"))][
                    "rev"
                ] += (float(order.total_price) if order.total_price else 0)
    print(len(cohort))


res = []

for phone, value in cohort.items():
    name = None
    profile_obj = Profile.objects.filter(phone_number=phone).first()
    if profile_obj:
        name = profile_obj.name
    if not name:
        user_obj = User.objects.filter(phone=phone).first()
        if user_obj:
            name = user_obj.name
    for week, value2 in value.items():
        res.append([phone, name, week, value2["count"], value2["rev"]])

df = pd.DataFrame(res)
df.to_excel("cohort_data.xlsx")
