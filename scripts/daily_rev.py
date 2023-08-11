from colorama import Fore
from shop.models import *

orders = (
    Order.objects.filter(created_on__gte="2022-4-26", created_on__lt="2022-4-27")
    .exclude(source__isnull=True)
    .exclude(payment_status__in=["CHECKOUT", "FAILED"])
)

rev = 0
payment_pending = 0
undelivered_orders = 0
time_unmarked = 0
for order in orders:
    if order.payment_status == "SUCCESS":
        print(
            Fore.GREEN
            + str(
                [
                    order.id,
                    order.customer.name,
                    order.customer.phone_number,
                    order.source,
                    order.total_price,
                    order.delivered_by.name if order.delivered_by else "NA",
                    order.delivered,
                    order.payment_status,
                    order.mode_of_payment,
                ]
            )
        )
    else:
        payment_pending += 1
        print(
            Fore.RED
            + str(
                [
                    order.id,
                    order.customer.name,
                    order.customer.phone_number,
                    order.source,
                    order.total_price,
                    order.delivered_by.name if order.delivered_by else "NA",
                    order.delivered,
                    order.payment_status,
                    order.mode_of_payment,
                ]
            )
        )
    rev += float(order.total_price) if order.total_price else 0
    if not order.delivered:
        undelivered_orders += 1
    if not order.delivery_time:
        time_unmarked += 1

print(f"revenue-{rev}")
print(f"count-{orders.count()}")
aov = rev / orders.count()
print(f"AOV-{aov}")
print(f"PAYMENT PENDING orders count {payment_pending}")
print(f"Undelivered orders count {undelivered_orders}")
print(f"time unmarked orders count {time_unmarked}")
