from shop.models import *
from account.models import *
import pandas as pd
import json


def order_data_mapping():
    details = []
    orders = Order.objects.all()
    for order in orders:
        temp_data = {
            "id": order.id,
            "mode_of_payment": order.mode_of_payment,
            "source": order.source,
            "payment_status": order.payment_status,
        }
        details.append(temp_data)

    with open("order_detail.json", "w") as data:
        json.dump(details, data, indent=6)


def fill_order_details():
    with open("order_detail.json", "r") as f:
        data = json.load(f)
    for order in data:
        if order["mode_of_payment"] == "Cash" or order["mode_of_payment"] == "CASH":
            order["mode_of_payment"] = "cash"
        if order["mode_of_payment"] == "UPI" or order["mode_of_payment"] == "Upi":
            order["mode_of_payment"] = "upi"
        if (
            order["mode_of_payment"] == "Netbanking"
            or order["mode_of_payment"] == "NETBANKING"
        ):
            order["mode_of_payment"] = "netbanking"
        if order["mode_of_payment"] == "Ecod" or order["mode_of_payment"] == "ecod":
            order["mode_of_payment"] = "electronic_cash_on_Delivery"
        if order["mode_of_payment"] == "Wallet" or order["mode_of_payment"] == "WALLET":
            order["mode_of_payment"] = "wallet"
        if order["mode_of_payment"] == "Card" or order["mode_of_payment"] == "CARD":
            order["mode_of_payment"] = "card"

        print(order["mode_of_payment"], order["id"])
        update_order = Order.objects.filter(id=order["id"]).update(
            mode_of_payment=order["mode_of_payment"],
            source=order["source"],
            payment_status=order["payment_status"],
        )
