from django.db import models
from phurti.models import TimeStamped
from .constants import ORDER_PLACED_WHATSAPP, ORDER_PLACED_SMS


class SMSTemplate(TimeStamped):
    title = models.CharField(max_length=50, db_index=True, null=True)
    body = models.TextField(max_length=500, blank=True)
