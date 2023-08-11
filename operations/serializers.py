from rest_framework import serializers
from .models import *
from shop import models
from account import models as account_models


class DeliveryExecutiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_models.Profile
        fields = ["phone_number", "name"]

    name = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=200)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_models.Profile
        fields = ["name", "phone_number", "id"]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_models.Profile
        fields = ["name", "phone_number"]


class AssignOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ["delivered_by", "order_id"]
