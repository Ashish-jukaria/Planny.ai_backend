from shop.models import *
from pyfcm import FCMNotification
from django.conf import settings

push_service = FCMNotification(api_key=settings.FCM_API_KEY)
import logging

logger = logging.getLogger("phurti")
INV_TO_BE_SKIPPED = ["old Whitefield"]
THRESHOLD_QUANTITY_REMAINING = 3
MAX_NO_OF_PRODUCTS = 10


def generate_notification_body(sellable_inventorys):
    body = []
    for sellable_inventory in sellable_inventorys:
        body.append(
            str(
                sellable_inventory.product.product_name
                + "("
                + str(sellable_inventory.quantity_remaining)
                + ")"
            )
        )
    return "\n".join(body)


def check_sellable_inventory():
    inventorys = Inventory.objects.all()
    for inventory in inventorys:
        if inventory.name not in INV_TO_BE_SKIPPED:
            si = SellableInventory.objects.filter(inventory_id=inventory.id)
            low_quantity_si = si.filter(
                quantity_remaining__lte=THRESHOLD_QUANTITY_REMAINING
            )[:MAX_NO_OF_PRODUCTS]
            from django.db.models import Q

            users = Profile.objects.filter(
                Q(inventory=inventory, role="SK") | Q(role="ADMIN")
            )
            device_ids = []
            for user in users:
                device_ids.append(user.device_id)
            message_title = "STOCKING ALERT !!!!!"
            message_body = generate_notification_body(low_quantity_si)
            result = push_service.notify_multiple_devices(
                registration_ids=device_ids,
                message_title=message_title,
                message_body=message_body,
            )
