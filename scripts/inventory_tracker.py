from shop.models import *
from django.utils.timezone import make_aware
import json
import pandas
from django.utils import timezone


def daily_inventory_tracker():
    today = timezone.now()
    yesturday = today - datetime.timedelta(days=1)
    stock = Stock.objects.filter(created_on__gte=yesturday).filter(
        created_on__lte=today
    )  # for getting all the product stocked today

    data = {}

    for j in stock:
        if j.product.description:
            des = "(" + str(j.product.description) + ")"
        else:
            des = ""

        invoice_item = (
            InvoiceItem.objects.filter(created_on__gte=yesturday)
            .filter(created_on__lte=today)
            .filter(product_id=j.product)
        )  # Getting billed invoice product by customers

        if j.product.id not in data:
            data[j.product.id] = {
                "Quantity Procured": Decimal(0),
                "Quantity Billed": Decimal(0),
                "Total Quantity Remaining": Decimal(0),
                "products_contained": [],
                "Inventory": j.inventory,
                "Product": j.product,
                "Unit": j.units,
            }
        for i in invoice_item:
            if j.product.id in data:
                if i.id not in data[j.product.id]["products_contained"]:
                    data[j.product.id]["products_contained"].append(i.id)
                    data[j.product.id]["Quantity Billed"] += i.quantity

        if j.product.id in data:
            data[j.product.id]["Quantity Procured"] += j.quantity
        else:
            data[j.product.id]["Quantity Procured"] += j.quantity

        data[j.product.id]["Total Quantity Remaining"] = (
            data[j.product.id]["Quantity Procured"]
            - data[j.product.id]["Quantity Billed"]
        )

    for stock in data:
        daily_tracker = DailyInventoryTracker.objects.create(
            inventory_id=data[stock]["Inventory"],
            product_id=data[stock]["Product"],
            quantity_unit=data[stock]["Unit"],
            quantity_remaining=data[stock]["Total Quantity Remaining"],
        )

        daily_tracker.save()
        print("Daily Tracker Created for:", data[stock]["Product"])
