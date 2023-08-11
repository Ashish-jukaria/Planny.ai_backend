import re
from django.http import response
from rest_framework import serializers
from account.models import *
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from shop.models import Inventory, Payment
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class Registration(serializers.ModelSerializer):
    email = serializers.EmailField(
        style={"input_type": "email"}, write_only=True, required=False
    )
    name = serializers.CharField(max_length=100, required=True, allow_blank=True)
    address = serializers.CharField(max_length=100, required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = (
            "phone_number",
            "name",
            "email",
            "role",
            "address",
            "inventory",
            "device_id",
        )

    def save(self):
        response = {"status": status.HTTP_400_BAD_REQUEST, "data": {}}

        email = self.validated_data.get("email", "")

        if Profile.objects.filter(
            phone_number=self.validated_data["phone_number"]
        ).exists():
            response["data"]["phone_number"] = ["Phone number already used"]
            raise serializers.ValidationError(response)

        if (
            Profile.objects.exclude(email__isnull=True)
            .exclude(email__exact="")
            .filter(email=email)
            .count()
            > 0
        ):
            response["data"]["email"] = ["Email already exist"]
            raise serializers.ValidationError(response)

        user = Profile(
            name=self.validated_data["name"],
            phone_number=self.validated_data["phone_number"],
            email=email,
            role=self.validated_data["role"],
            inventory=self.validated_data["inventory"],
            device_id=self.validated_data["device_id"],
        )
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


class AlternativeSerializer(serializers.ModelSerializer):
    pk = serializers.CharField(max_length=50, allow_blank=True, allow_null=True)


class UserProfileSerializer(serializers.ModelSerializer):
    inventory = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "phone_number",
            "name",
            "email",
            "role",
            "inventory",
            "id",
            "attributes",
        ]

    def get_inventory(self, obj):
        if obj.inventory:
            inv = Inventory.objects.get(pk=obj.inventory.id)
            return {"name": inv.name, "code": inv.code, "id": inv.id}
        return obj.inventory


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class WalletMiniSerializer(serializers.Serializer):
    amount = serializers.CharField(max_length=50)
    transaction_type = serializers.CharField(max_length=50)
    order_id = serializers.IntegerField()


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            "id",
            "title",
            "description",
            "custom_domain",
            "address",
            "logo_url",
            "subdomain",
            "tenant_category",
        ]


class TenantCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantCategory
        fields = "__all__"


class TenantRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = TenantUser
        fields = ["password", "phone_number", "name", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = TenantUser.objects.create(
            phone_number=validated_data["phone_number"],
            name=validated_data["name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class TenantUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=HUNDRED, required=True, allow_blank=True)

    class Meta:
        model = TenantUser
        fields = ["password", "phone_number", "name", "username"]
        extra_kwargs = {"password": {"write_only": True}}


class TenantUserDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=HUNDRED, required=False, allow_blank=True)

    class Meta:
        model = TenantUser
        fields = ["phone_number", "name", "username"]
        # extra_kwargs = {'password': {'write_only': True}}


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionDetail
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
