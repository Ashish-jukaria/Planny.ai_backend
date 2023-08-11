from rest_framework import serializers
from phurti.constants import *
from payments import gateways


class PaymentSerializer:
    gateway = serializers.CharField(max_length=HUNDRED, allow_null=False)
    data = serializers.JSONField(allow_null=False)

    class Meta:
        fields = "__all__"
