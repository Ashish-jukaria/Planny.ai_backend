from django.db import models
from phurti.models import TimeStamped
from .constants import *


class Customer(TimeStamped):
    name = models.CharField("Name", blank=True, max_length=100, db_index=True)
    email = models.CharField(
        "Email", blank=True, null=True, max_length=100, db_index=True, unique=True
    )
    phone = models.CharField(
        "Mobile Number",
        blank=True,
        null=True,
        max_length=50,
        db_index=True,
        unique=True,
    )
    address = models.TextField(default="")
    last_login = models.DateTimeField("last login", blank=True, null=True)
    is_active = models.BooleanField(default=1)  # 1: Active, 0: In Active

    def __str__(self):
        return f"{self.name}:{self.phone}"


class Alternative(TimeStamped):
    customer = models.ForeignKey(
        Customer, related_name="alternatives", on_delete=models.CASCADE
    )
    type = models.IntegerField("Alternative Type", default=1, choices=ALTERNATIVE_TYPES)
    value = models.CharField(
        "Email or Phone", blank=False, null=False, max_length=255, db_index=True
    )
    primary = models.BooleanField("Is Primary?", default=False)
    verified = models.BooleanField("Is Verified?", default=False)
    active = models.BooleanField("Is Active?", default=True)
    label = models.CharField(
        "label", max_length=255, null=True, blank=True, choices=ALTERNATE_LABEL
    )
