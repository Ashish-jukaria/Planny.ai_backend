from django.db import models
from django.utils import timezone
from phurti.constants import *


class TimeStamped(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Channel(TimeStamped):
    name = models.CharField(max_length=HUNDRED)
    phone_number = models.CharField(max_length=TWENTY, unique=True)
    license_number = models.CharField(max_length=HUNDRED)
    gst_number = models.CharField(max_length=FIFTY)
    address = models.TextField()
    is_active = models.BooleanField()

    def __str__(self) -> str:
        return self.name