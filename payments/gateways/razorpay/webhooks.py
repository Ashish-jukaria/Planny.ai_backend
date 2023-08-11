from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from datetime import datetime
from pytz import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from phurti import settings
from shop.models import Order, Payment
from payments.constants import *
import razorpay
import logging
import json

logger = logging.getLogger("phurti")


@api_view(["POST"])
@csrf_exempt
def webhook_receiver(request):
    try:
        # Webhook Details
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        webhook_body = str(request.body, "utf-8")
        webhook_signature = request.headers["X-Razorpay-Signature"]

        # Creating Razorpay Client
        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY)
            )
        except Exception as e:
            logger.error("Razorapy Client not created", e)
            return Response(
                {"message": "Razorpay Server Down"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Verifying webhook signature
        try:
            check = client.utility.verify_webhook_signature(
                webhook_body, webhook_signature, webhook_secret
            )
        except Exception as e:
            logger.error("Error while verifying webhook", e)
            return Response(
                {"message": "Not from Razorpay"}, status=status.HTTP_403_FORBIDDEN
            )

        if check == None:
            webhook_body = json.loads(request.body)
            # Webhook event type
            event = webhook_body["event"]

            # Payment Entity
            payment_entity = webhook_body["payload"]["payment"]["entity"]

            # Razorpay Payment Details
            razorpay_payment_id = payment_entity["id"]
            payment_status = payment_entity["status"]
            payment_method = payment_entity["method"]

            if event == INV_PAID:
                # Invoice Entity
                invoice_entity = webhook_body["payload"]["invoice"]["entity"]

                # Invoice Details
                payment_type = invoice_entity["type"]

                # Order ID and Payment ID
                order_id = invoice_entity["notes"]["order_id"]
                payment_id = invoice_entity["notes"]["payment_id"]

                # Get Order and update Details
                order = Order.objects.get(pk=order_id)
                order.mode_of_payment = payment_method
                order.save()

                # Get Payment and Update Details
                payment = Payment.objects.get(pk=payment_id)
                payment.amount = order.total_price
                payment.payment_id = razorpay_payment_id
                payment.source = order.source
                payment.gateway_type = RAZORPAY
                payment.mode = payment_method
                payment.additional_details = payment.additional_details + json.dumps(
                    payment_entity
                )
                payment.save()

                if payment_type == LINK:
                    if payment_status == CAPTURED:
                        # Updating Payment Details
                        payment.status = SUCCESS
                        payment.payment_date = str(datetime.now())
                        payment.save()

                        # Updating Order Details
                        order.payment_status = SUCCESS
                        order.save()
                        return HttpResponse(status=200)
                    else:
                        logger.error("Payment not captured")
                        return HttpResponse(status=400)
            elif event == PAYMENT_CAPTURED:
                return HttpResponse(status=200)
            elif event == PAYMENT_FAILED:
                return HttpResponse(status=200)
                payment_method = payment_entity["method"]
                # Getting Invoice ID
                payment_desc = payment_entity["description"]
                razorpay_invoice_id = "inv_" + payment_desc[1:]
                print(razorpay_invoice_id)
                # Invoice Entity
                invoice_entity = client.invoice.fetch(razorpay_invoice_id)
                print(invoice_entity)
                # Order ID and Payment ID
                order_id = invoice_entity["notes"]["order_id"]
                payment_id = invoice_entity["notes"]["payment_id"]

                # Get Order and update Details
                order = Order.objects.get(pk=order_id)
                order.mode_of_payment = payment_method
                order.payment_status = FAILED
                order.save()

                # Get Payment and Update Details
                payment = Payment.objects.get(pk=payment_id)
                payment.amount = order.total_price
                payment.payment_id = razorpay_payment_id
                payment.source = order.source
                payment.gateway_type = RAZORPAY
                payment.mode = payment_method
                payment.additional_details = json.dumps(payment_entity)
                payment.status = FAILED
                payment.payment_date = str(datetime.now())
                payment.save()
                logger.error("Payment Failed")
                return HttpResponse(status=200)
        else:
            logger.error("Webhook Signature mismatch")
            return HttpResponse(status=400)
    except Exception as e:
        logger.error("Webhook Receiver error", e)
        return HttpResponse(status=400)
