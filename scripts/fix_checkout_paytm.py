from base import django_env

django_env()
import sys
from shop.models import *
import json
from shop.views import update_inventory
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger("phurti")
import paytmchecksum
import phurti.settings as settings
from payments.constants import *

PAYTM_MID = settings.PAYTM_MERCHANT_ID
PAYTM_MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
PAYTM_WEBISTE = settings.PAYTM_WEBSITE
PAYTM_HOST = settings.PAYTM_HOST


def get_payment(order_id):
    import requests
    import json

    # import checksum generation utility
    # You can get this utility from https://developer.paytm.com/docs/checksum/

    # initialize a dictionary
    paytmParams = dict()

    # body parameters
    paytmParams["body"] = {
        "mid": PAYTM_MID,
        "orderId": order_id,
    }

    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
    checksum = paytmchecksum.generateSignature(
        json.dumps(paytmParams["body"]), PAYTM_MERCHANT_KEY
    )

    # head parameters
    paytmParams["head"] = {
        # put generated checksum value here
        "signature": checksum
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    # for Staging
    url = f"{PAYTM_HOST}/v3/order/status"

    # for Production
    # url = "https://securegw.paytm.in/v3/order/status"

    response = requests.post(
        url, data=post_data, headers={"Content-type": "application/json"}
    ).json()
    return response


def fix_payment():
    try:
        orderId = sys.argv[1]
        update_sellable = sys.argv[2]

        if update_sellable.lower() == "true":
            update_sellable = True

        elif update_sellable == "1":
            update_sellable = True

        else:
            update_sellable = False

        response = get_payment(orderId)
        if (
            response
            and response["body"]
            and response["body"]["resultInfo"]
            and response["body"]["resultInfo"]["resultStatus"] == TXN_SUCCESS
        ):
            # Updating Payment Details"
            order = Order.objects.filter(pk=int(orderId)).first()
            payment = Payment.objects.filter(order=order).first()
            payment.status = SUCCESS
            payment.payment_id = response["body"]["txnId"]
            payment.payment_date = str(timezone.now())
            payment.mode = PAYTM_PAYMENT_CODE[response["body"]["paymentMode"]]
            payment.additional_details = json.dumps(response["body"])
            payment.save()

            # Updating Order Details
            order.mode_of_payment = PAYTM_PAYMENT_CODE[response["body"]["paymentMode"]]
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
            logger.error("Payment is not valid or it is a failed payment id.")

    except Exception as e:
        logger.error(e)
        print("Check the log for errors!")
        print("ERRORS:", e)


fix_payment()
