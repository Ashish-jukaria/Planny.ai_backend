from base import django_env

django_env()
import sys
import razorpay
from shop.models import *
import json
from shop.views import update_inventory
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger("phurti")


def fix_payment():
    try:
        paymentId = sys.argv[1]
        update_sellable = sys.argv[2]
        if update_sellable.lower() == "true":
            update_sellable = True

        elif update_sellable == "1":
            update_sellable = True

        else:
            update_sellable = False

        client = razorpay.Client(
            auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY)
        )
        response = client.payment.fetch(paymentId)

        if response and response["captured"]:
            # Updating Payment Details"
            order = Order.objects.filter(pk=response["notes"]["order_id"]).first()
            payment = Payment.objects.filter(order=order).first()
            payment.status = SUCCESS
            payment.payment_id = response["id"]
            payment.payment_date = str(timezone.now())
            payment.mode = response["method"]
            payment.additional_details = json.dumps(response)
            payment.save()

            # Updating Order Details
            order.mode_of_payment = response["method"]
            order.payment_status = SUCCESS
            order.save()

            try:
                if update_sellable:
                    update_inventory(order)
            except Exception as e:
                logger.error(e)

            # Updating Cart details and removing the cart
            cart = Cart.objects.filter(customer=order.customer).last()
            cart.cartitem.all().update(is_active=False)
            cart.status = ORDER_PLACED
            cart.save()
            print("UPDATED SUCCESSFULLY!")
        else:
            logger.log("Payment is not valid or it is a failed payment id.")

    except Exception as e:
        logger.error(e)
        print("Check the log for errors!")
        print("ERRORS:", e)


fix_payment()
