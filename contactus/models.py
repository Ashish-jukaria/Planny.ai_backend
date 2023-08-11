from django.db import models
from django.core.validators import RegexValidator
from django.utils.timezone import localtime
from phurti.models import TimeStamped
from shop.models import *


class Items(TimeStamped):
    order_name = models.CharField(max_length=100, blank=True, default="None")
    price = models.FloatField()
    # discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.order_name


class CallbackRequest(TimeStamped):
    name = models.CharField(max_length=50, blank=False)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{10,15}$",
        message="Phone number must be entered in the format: '987654321'. Up to 15 digits allowed.",
    )
    phone = models.CharField(validators=[phone_regex], max_length=17)
    call_delivered = models.BooleanField(default=False, blank=True)
    address = models.TextField(max_length=100, null=True, blank=True, default="")
    inventory_id = models.ForeignKey(
        Inventory, null=True, blank=True, on_delete=models.SET_NULL
    )

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     "notification mechanism here"
    #     pass

    def __str__(self):
        return "{0} requested callback on {1}".format(
            self.name, localtime(self.created_on).strftime(STATE_DATE_FORMAT)
        )
