import json
from django.shortcuts import render
from .models import SMSTemplate
from .constants import ORDER_PLACED_WHATSAPP, ORDER_PLACED_SMS, ORDER_CONFIRMATION
from django.conf import settings
from rest_framework.response import Response
from phurti.constants import COD, CASH
from shop.constants import BILL
import logging
from .utils import change_for_whatsapp, parse_number
from twilio.rest import Client
from django.template import Template, Context
import razorpay

# Create your views here.

logger = logging.getLogger("phurti")


def get_template(order):
    if order.source == BILL:
        return SMSTemplate.objects.get(title=ORDER_PLACED_WHATSAPP)
    if order.mode_of_payment == CASH:
        return SMSTemplate.objects.get(title=ORDER_PLACED_SMS)
    else:
        return SMSTemplate.objects.get(title=ORDER_CONFIRMATION)


def send_order_communication(order, payment):
    try:
        ##GETTING MESSAGE TEMPLATE
        sms_template_object = get_template(order)
        if sms_template_object:
            print(sms_template_object)
            message_body = sms_template_object.body
            sender = settings.SENDER_SMS
            phone_number = parse_number(order.customer.phone_number)
            receiver = "+91" + f"{phone_number}"
            invoice_link = settings.INVOICE_LINK + f"{order.id}"

            message_details = {
                "username": order.customer.name,
                "order_no": order.id,
                "total_price": order.total_price,
                "invoice_link": invoice_link,
            }

            # generate payment link and modify body attach payment link
            sender = change_for_whatsapp(sender)
            receiver = change_for_whatsapp(receiver)
            if order.source == BILL or order.mode_of_payment == CASH:
                try:
                    client = razorpay.Client(
                        auth=(
                            settings.RAZORPAY_API_KEY,
                            settings.RAZORPAY_API_SECRET_KEY,
                        )
                    )  # import from settings
                except Exception as e:
                    logger.error(e)

                customer_name = str(order.customer.name)
                amount = int(order.total_price) * 100
                customer = order.customer

                payment_data = {
                    "customer": {
                        "name": customer_name,  # Change to customer name
                        "email": customer.email,
                        "contact": customer.phone_number,
                    },
                    "type": "link",
                    "amount": amount,  # Change to total order amount
                    "currency": "INR",
                    "description": "Payment for PHURTI",  # Attach order_id
                    "notes": {"order_id": order.id, "payment_id": payment.id},
                }

                try:
                    payment_link_data = client.invoice.create(data=payment_data)
                    payment.additional_details = json.dumps(payment_link_data)
                    payment.save()
                    payment_link = payment_link_data["short_url"]  # Add to message body
                except Exception as e:
                    logger.error(e)

                ##ADDING PAYMENT LINK TO THE MESSAGE DEATAILS"
                message_details["payment_link"] = payment_link

            message_body = Template(message_body)
            message_body = message_body.render(Context(message_details))

            # using messaging service - currently twilio
            try:
                client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
                message = client.messages.create(
                    from_=sender, body=message_body, to=receiver
                )
            except Exception as e:
                logger.error(e)

    except Exception as e:
        logger.error(e)
