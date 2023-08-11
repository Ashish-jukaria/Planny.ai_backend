from shop.utils import *
from django.utils.timezone import make_aware
from django.conf import settings
import datetime
import logging

request_logger = logging.getLogger("request_filter")


class OperationsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        try:
            if hasattr(response, "data"):
                try:
                    operational = True
                    if request and request.user and not request.user.is_anonymous:
                        if request.user.inventory.is_active:
                            operational = True
                        else:
                            if (
                                request.user.phone_number
                                not in settings.BYPASS_INV_LOCK
                            ):
                                operational = False
                except Exception as e:
                    request_logger.error(str(e))

                response.data["server time"] = str(make_aware(datetime.datetime.now()))
                response.data["operational"] = operational
                response.data["unoperational_message"] = settings.UNOPERATIONAL_MESSAGE
                response.data["delivery_charge"] = get_delivery_charge()
                response.data["default_delivery_charge"] = get_default_delivery_charge()
                response.data["start_time"] = get_deliverychange_time()
                response.data["inventory_status"] = get_inventory_status()

        except Exception as e:
            request_logger.error(str(e))

        return response
