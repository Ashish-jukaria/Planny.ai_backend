from shop.models import *
import datetime
from django.utils.timezone import make_aware
from decimal import Decimal
import json
import pandas
from django.utils import timezone
from .views import OTPsend
from django.conf import settings
import os
from dateutil import parser


def create_subs_order():
    today = datetime.date.today()
    tommorow = today + datetime.timedelta(days=1)
    active_subscription = (
        Subscriptions.objects.filter(is_active=True)
        .filter(to_date__gte=tommorow)
        .filter(from_date__lte=tommorow)
    )

    # try:

    for i in active_subscription:
        createTime = datetime.datetime.combine(tommorow, i.time_slot)
        awarecreateTime = make_aware(createTime)

        # This is for backward compatibility for creating orders for previous user's
        if i.customer:
            name = i.customer.name
            phone = i.customer.phone
            delivery_type = DeliveryType.objects.filter(type="EXPRESS").first()
            user = User.objects.filter(name=name, phone=phone)
            if user:
                user = user.first()
            else:
                user = User.objects.create(name=name, phone=phone)
                user.save()
            cart = Cart.objects.create(
                user=user,
            )
            for pro in i.products.all():
                cartitem = CartItem.objects.create(
                    product=pro, user=user, quantity=i.quantity
                )
                cartitem.save()
                cart.cartitem.add(cartitem)

            cart.save()
            order = Order.objects.create(
                user=user,
                cart=cart,
            )
            # Updating all active items to false
            Cart.objects.filter(pk=cart.id).first().cartitem.all().update(
                is_active=False
            )

            # getting all orderlist as string here
            ordercontent = Cart.objects.filter(pk=cart.id).first().get_order_list()

            # Total price get
            totalprice = Cart.objects.filter(pk=cart.id).first().get_total_price()

            # changing the staus to "ORDERED"
            Cart.objects.filter(pk=cart.id).update(status="ORDER_PLACED")

            # getting the extra address field

            order.checkout_address = i.customer.address
            order.orderlist = ordercontent
            order.delivery_type = delivery_type
            order.total_price = totalprice + Decimal(10)
            order.created_on = awarecreateTime
            order.inventory = i.inventory
            order.save()

            print("Order Created succesfully")

        # for user which are created on admin's default user
        elif i.new_customer:
            customer = i.new_customer
            delivery_type = DeliveryType.objects.filter(type="EXPRESS").first()
            cart = Cart.objects.create(
                customer=customer,
            )
            for pro in i.products.all():
                cartitem = CartItem.objects.create(
                    product=pro, customer=customer, quantity=i.quantity
                )
                cartitem.save()
                cart.cartitem.add(cartitem)

            cart.save()
            order = Order.objects.create(customer=customer, cart=cart)
            # Updating all active items to false
            Cart.objects.filter(pk=cart.id).first().cartitem.all().update(
                is_active=False
            )

            # getting all orderlist as string here
            ordercontent = Cart.objects.filter(pk=cart.id).first().get_order_list()

            # Total price get
            totalprice = cart.get_total_price(cartitems=cart.cartitem.all())

            # changing the staus to "ORDERED"
            Cart.objects.filter(pk=cart.id).update(status="ORDER_PLACED")

            # getting the extra address field

            order.checkout_address = i.new_customer.address
            order.orderlist = ordercontent
            order.delivery_type = delivery_type
            order.total_price = Decimal(totalprice) + Decimal(10)
            order.created_on = awarecreateTime
            order.inventory = i.inventory
            order.save()

            print("Order Created succesfully")

    # except:
    #     print("Error on creating order")


def deactivate_subscription():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    subs = Subscriptions.objects.filter(to_date=yesterday)
    for j in subs:
        j.is_active = False
        j.save()


def create_subs_order_daterange():
    today = datetime.date.today()
    tommorow = today + datetime.timedelta(days=1)

    day_count = (today - (today - datetime.timedelta(days=36))).days + 1

    main_date = today - datetime.timedelta(days=36)
    for j in range(day_count):
        active_subscription = (
            Subscriptions.objects.filter(is_active=True)
            .filter(from_date__lte=main_date + datetime.timedelta(j))
            .filter(to_date__gte=main_date + datetime.timedelta(j))
            .filter(created_on__date=today)
        )
        print(main_date + datetime.timedelta(j))
        for i in active_subscription:
            createTime = datetime.datetime.combine(
                main_date + datetime.timedelta(j), i.time_slot
            )
            awarecreateTime = make_aware(createTime)
            name = i.customer.name
            phone = i.customer.phone
            delivery_type = DeliveryType.objects.filter(type="EXPRESS").first()
            user = User.objects.filter(name=name, phone=phone)
            if user:
                user = user.first()
            else:
                user = User.objects.create(name=name, phone=phone)
                user.save()
            cart = Cart.objects.create(
                user=user,
            )
            for pro in i.products.all():
                cartitem = CartItem.objects.create(product=pro, user=user)
                cartitem.save()
                cart.cartitem.add(cartitem)

            cart.save()
            order = Order.objects.create(
                user=user,
                cart=cart,
            )
            # Updating all active items to false
            Cart.objects.filter(pk=cart.id).first().cartitem.all().update(
                is_active=False
            )

            # getting all orderlist as string here
            ordercontent = Cart.objects.filter(pk=cart.id).first().get_order_list()

            # Total price get
            totalprice = Cart.objects.filter(pk=cart.id).first().get_total_price()

            # changing the staus to "ORDERED"
            Cart.objects.filter(pk=cart.id).update(status="ORDER_PLACED")

            # getting the extra address field

            order.checkout_address = i.customer.address
            order.orderlist = ordercontent
            order.delivery_type = delivery_type
            order.total_price = totalprice
            order.created_on = awarecreateTime
            order.save()

            print("Order Created succesfully", user)


# def profit_stock():
#     # import ipdb
#     # ipdb.set_trace()
#     today = timezone.now()
#     yesturday = today - datetime.timedelta(days=1)
#     stock = Stock.objects.filter(created_on__gte=yesturday).filter(created_on__lte=today) #for getting all the product stocked today


#     data = {}

#     for j in stock:
#         if j.product.description: des = "(" + str(j.product.description) + ")"
#         else: des = ""

#         invoice_item = InvoiceItem.objects.filter(created_on__gte=yesturday).filter(created_on__lte=today).filter(product_id=j.product) # Getting billed invoice product by customers

#         money_spend_temp = j.quantity*Decimal(j.procurement_price_per_product)

#         money_recieved_temp = Decimal(0) # Total money received by customer
#         if j.product.id not in data:
#                 data[j.product.id] = {
#                     "Product Id": '',
#                     "Product": '',
#                     "Quantity Procured": Decimal(0),
#                     "Quantity Procured Unit": '',
#                     "Quantity Billed": Decimal(0),
#                     "Quantity Billed Unit": '',
#                     "Total Money Received": Decimal(0),
#                     "Total Money Spend": Decimal(0),
#                     "Total Quantity Remaining": Decimal(0),
#                     "Total Quantity Remaining Unit": '',
#                     "products_contained": [],

#                 }
#                 data[j.product.id]["Product Id"] = j.product.id
#                 data[j.product.id]["Product"] = str(j.product.product_name)+des
#                 data[j.product.id]["Quantity Procured Unit"] = j.units.unit
#         for i in invoice_item:
#             if j.product.id in data:
#                 if i.id not in data[j.product.id]["products_contained"]:
#                     data[j.product.id]["products_contained"].append(i.id)
#                     data[j.product.id]["Quantity Billed"] += i.quantity

#             money_recieved_temp+=(i.quantity*i.product_id.price) # Total money received by customer


#         if j.product.id in data:

#             data[j.product.id]["Total Money Received"] = money_recieved_temp
#             data[j.product.id]["Quantity Procured"] += j.quantity
#             data[j.product.id]["Total Money Spend"] += money_spend_temp
#             data[j.product.id]["Total Quantity Remaining Unit"] = j.units.unit
#         else:
#             data[j.product.id]["Quantity Procured"] += j.quantity
#             data[j.product.id]["Total Money Spend"] += money_spend_temp


#         if invoice_item.first():
#             if invoice_item.first().unit_id:
#                 if j.product.id in data:
#                     data[j.product.id]["Quantity Billed Unit"] = invoice_item.first().unit_id.unit
#             else:
#                 data[j.product.id]["Quantity Billed Unit"] = "N/A"
#         else:
#             if j.product.id in data:
#                 data[j.product.id]["Quantity Billed Unit"] = "N/A"

#         data[j.product.id]["Total Quantity Remaining"] = data[j.product.id]["Quantity Procured"] - data[j.product.id]["Quantity Billed"]


#         print("\n",j.product.product_name, "\n")

#     df = pandas.DataFrame(data=data)

#     df.T.to_excel(str(datetime.date.today())+".xlsx")


order_id = [
    9156,
    9155,
    9154,
    9146,
    9105,
    9102,
    9091,
    9111,
    9052,
    9002,
    9004,
    9003,
    8980,
    8818,
    8754,
    8861,
    9053,
    8931,
    8743,
    8758,
    8741,
    8831,
    9013,
    9158,
]
from django.db.models import Q


def profit_stock(invid):
    today = datetime.datetime(2021, 10, 27, 20, 0)
    stock = Stock.objects.filter(
        created_on__gte=today, inventory_id=invid
    )  # for getting all the product stocked today

    data = {}

    for j in stock:
        if j.product.description:
            des = "(" + str(j.product.description) + ")"
        else:
            des = ""

        if invid == 1:
            invoice_item = (
                InvoiceItem.objects.filter(created_on__gte=today)
                .filter(product_id=j.product)
                .filter(~Q(invoice_id__order_id__in=order_id))
            )  # Getting billed invoice product by customers
        else:
            invoice_item = (
                InvoiceItem.objects.filter(created_on__gte=today)
                .filter(product_id=j.product)
                .filter(Q(invoice_id__order_id__in=order_id))
            )

        wastage = WastedProduct.objects.filter(created_on__gte=today).filter(
            product_id=j.product
        )  # Getting wastage product

        money_spend_temp = j.quantity * Decimal(j.procurement_price_per_product)

        money_recieved_temp = Decimal(0)  # Total money received by customer
        if j.product.id not in data:
            data[j.product.id] = {
                "Product Id": "",
                "Product": "",
                "Quantity Procured": Decimal(0),
                "Quantity Procured Unit": "",
                "Quantity Billed": Decimal(0),
                "Quantity Billed Unit": "",
                "Total Money Received": Decimal(0),
                "Total Money Spend": Decimal(0),
                "Total Quantity Remaining": Decimal(0),
                "Total Quantity Remaining Unit": "",
                "products_contained": [],
            }
            data[j.product.id]["Product Id"] = j.product.id
            data[j.product.id]["Product"] = str(j.product.product_name) + des
            data[j.product.id]["Quantity Procured Unit"] = j.units.unit
        for i in invoice_item:
            if j.product.id in data:
                if i.id not in data[j.product.id]["products_contained"]:
                    data[j.product.id]["products_contained"].append(i.id)
                    data[j.product.id]["Quantity Billed"] += i.quantity

            money_recieved_temp += (
                i.quantity * i.product_id.price
            )  # Total money received by customer

        for waste in wastage:
            if j.product.id in data:
                if waste.id not in data[j.product.id]["products_contained"]:
                    data[j.product.id]["wasted"] += waste.quantity

        if j.product.id in data:
            data[j.product.id]["Total Money Received"] = money_recieved_temp
            data[j.product.id]["Quantity Procured"] += j.quantity
            data[j.product.id]["Total Money Spend"] += money_spend_temp
            data[j.product.id]["Total Quantity Remaining Unit"] = j.units.unit
        else:
            data[j.product.id]["Quantity Procured"] += j.quantity
            data[j.product.id]["Total Money Spend"] += money_spend_temp

        if invoice_item.first():
            if invoice_item.first().unit_id:
                if j.product.id in data:
                    data[j.product.id][
                        "Quantity Billed Unit"
                    ] = invoice_item.first().unit_id.unit
            else:
                data[j.product.id]["Quantity Billed Unit"] = "N/A"
        else:
            if j.product.id in data:
                data[j.product.id]["Quantity Billed Unit"] = "N/A"

        data[j.product.id]["Total Quantity Remaining"] = data[j.product.id][
            "Quantity Procured"
        ] - (data[j.product.id]["Quantity Billed"] + data[j.product.id]["wasted"])

        print("\n", j.product.product_name, "\n")

    df = pandas.DataFrame(data=data)

    df.T.to_excel(str("INV0" + str(invid) + datetime.date.today()) + ".xlsx")


def f():
    inv = Inventory.objects.all()
    for i in inv:
        profit_stock(i.id)


def send_reminder():
    fname = "orderscheduler_data/scheduler.json"
    today = str(datetime.date.today())
    upper_limit = timezone.localtime() + datetime.timedelta(
        minutes=5
    )  # 10 s window upperlimit
    lower_limit = timezone.localtime() - datetime.timedelta(
        minutes=5
    )  # 10 minute window lowerlimit

    if os.path.isfile(fname):
        with open(fname) as task:
            schedulerd_data = json.load(task)
        # fromisoformat

        if today in schedulerd_data:
            for task in schedulerd_data[today]:
                if (
                    parser.parse(task["schedule_time"]) <= upper_limit
                    and parser.parse(task["schedule_time"]) >= lower_limit
                    and (task["OTP_sent"] == False)
                ):
                    OTPsend(settings.PHONES)  # Send OTP reminder for upcoming orders
                    print("<--------------OTP SENT-------------->")
                    task["OTP_sent"] = True

        with open(fname, mode="w") as f:
            f.write(json.dumps(schedulerd_data, indent=2))

    else:
        print("<--------------File Not Found-------------->")


def _time(time):
    return datetime.datetime.strptime(time, "%H:%M:%S")


def deactivate_inventory():
    import datetime

    INVENTORY = settings.INVENTORY
    current = datetime.datetime.strptime(
        datetime.datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S"
    )
    for j in INVENTORY:
        for i in INVENTORY[j]:
            if _time(i).time() < current.time():
                inv = Inventory.objects.get(id=int(j))
                inv.is_active = INVENTORY[j][i]
                inv.save()
                print(inv, i)
