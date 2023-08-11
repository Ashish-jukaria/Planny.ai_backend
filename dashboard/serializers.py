from shop.models import VariationOptions
from rest_framework import serializers

from shop.models import (
    VariationTypes,
    ProductPriceVariation,
    ProductVariation,
    Toppings,
    VariationCombos,
)


class VariationTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariationTypes
        fields = ["id", "name", "description", "is_active"]


class ProductPriceVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceVariation
        fields = "__all__"


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ["id", "tenant", "product", "price_variation", "is_active"]


class VariationOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariationOptions
        fields = "__all__"


class ToppingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toppings
        fields = ["id", "name", "tenant", "is_active", "image", "product", "price"]


class VariationCombosSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariationCombos
        fields = "__all__"
