from django.db.models import fields
from rest_framework import serializers
from .models import *


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ["order_name"]
