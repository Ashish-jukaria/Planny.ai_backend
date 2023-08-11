import re
from django.http import response
from rest_framework import serializers
from .models import *
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class Registration(serializers.ModelSerializer):
    email = serializers.EmailField(
        style={"input_type": "email"}, write_only=True, required=False
    )
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = Customer
        fields = ("phone", "username", "password", "password2", "email")
        extra_kwargs = {"password": {"write_only": True}}

    def save(self):
        response = {"status": status.HTTP_400_BAD_REQUEST, "data": {}}

        email = self.validated_data.get("email", "")
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if Customer.objects.filter(username=self.validated_data["username"]).exists():
            response["data"]["username"] = "Username already exist"
            raise serializers.ValidationError(response)

        if Customer.objects.filter(phone=self.validated_data["phone"]).exists():
            response["data"]["phone"] = "Phone number already used"
            raise serializers.ValidationError(response)

        if (
            Customer.objects.exclude(email__isnull=True)
            .exclude(email__exact="")
            .filter(email=email)
            .count()
            > 0
        ):
            response["data"]["email"] = "Email already exist"
            raise serializers.ValidationError(response)

        if password != password2:
            response["data"]["password"] = "Password Fields are not matched."
            raise serializers.ValidationError(response)

        user = Customer(
            username=self.validated_data["username"],
            phone=self.validated_data["phone"],
            email=email,
        )
        user.password = password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


class AlternativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternative
        fields = ("type", "value")
