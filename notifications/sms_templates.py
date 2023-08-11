from notifications.models import *
from notifications.constants import *

SMS_TEMPLTES = {
    "TITLE": ORDER_PLACED_WHTASAPP,
    "body": "hjgsdvcjsdkvghcsahcvdjsbvkshvbdfhjlbvdvfdvd",
}

for key, val in SMS_TEMPLTES.items():
    SMSTemplate.object.create(**val)
