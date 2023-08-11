from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator

# from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from .constants import SUCCESS, FAILED
from datetime import timedelta
from django.utils import timezone

# expirytime = timezone.now() + timedelta(minutes=7)
from django.db import transaction
from .utils import *
from phurti.models import TimeStamped
from phurti.constants import *
from customer.constants import *
from .constants import *
from shop.enums import *


class Staff(models.Model):
    title = models.CharField(max_length=30, choices=STAFF_CATEGORY)

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staffs"

    def __str__(self):
        return self.get_title_display()


class OTP(models.Model):
    OTP_CATEGORY = (("E", ("EMAIL")), ("S", ("SMS")), ("V", ("VOICE")))
    code = models.CharField(max_length=6)
    otp_verified = models.BooleanField(default=False)
    type = models.CharField(max_length=15, choices=OTP_CATEGORY)
    resend_count = models.CharField(max_length=10, default=3)
    # expiry = models.DateTimeField(default=expirytime)


phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '987654321'. Up to 15 digits allowed.",
)


class Profile(AbstractUser):
    DEFAULT_ATTRIBUTES = {
        "PHONE_NUMBERS": [
            {
                "id": 0,
                "phone_number": None,
                "primary": True,
                "label": None,
                "verified": True,
            }
        ],
        "EMAILS": [
            {"id": 0, "email": None, "primary": True, "label": None, "verified": True}
        ],
        "ADDRESSES": [
            {
                "id": 0,
                "address": None,
                "phone_number": None,
                "pincode": None,
                "landmark": None,
                "label": None,
                "primary": True,
                "verified": True,
            }
        ],
    }
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True
    )
    staff_category = models.ForeignKey(
        Staff, on_delete=models.CASCADE, null=True, blank=True
    )
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE, null=True, blank=True)
    username = models.CharField(
        max_length=40, unique=False, default="", blank=True
    )  # Username can be blank
    name = models.CharField(max_length=30, null=True, blank=True)  # Users name
    inventory = models.ForeignKey(
        "shop.Inventory",
        verbose_name="Area",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    device_id = models.CharField(max_length=TWO_HUNDRED, null=True, blank=True)
    attributes = models.JSONField(default=DEFAULT_ATTRIBUTES)

    tenant = models.ForeignKey("account.Tenant", on_delete=models.CASCADE, default=1)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.phone_number

    def get_active_order(self):
        active_orders_queryset = self.orders.filter(
            status__in=[
                Status.ORDER_PLACED.value,
                Status.INITIALISED.value,
                Status.INVOICE_GENERATED.value,
            ]
        )
        if active_orders_queryset:
            return active_orders_queryset.last()
        else:
            return


# class UserAddress(TimeStamped):
#     user = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name="user_addresses")
#     address = models.TextField()
#     landmark = models.CharField(max_length=TWO_HUNDRED)
#     is_primary = models.BooleanField(default=False)
#     latitude = models.DecimalField(max_digits=TWENTY, decimal_places=TEN, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=TWENTY, decimal_places=TEN, null=True, blank=True)
#     label = models.CharField(max_length=FIFTY, null=True, blank=True)
#     is_active = models.BooleanField(default=True)


class TransactionType(TimeStamped):
    title = models.CharField(max_length=FIFTY, choices=TRANSACTION_TYPES)

    def __str__(self):
        return self.title


class Wallet(TimeStamped):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name="User")
    balance = models.DecimalField(max_digits=TEN, decimal_places=TWO, default=ZERO)
    max_balance = models.DecimalField(
        max_digits=TEN, decimal_places=TWO, default=FIFTY_THOUSANDS
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user.name) + str(" balance: ") + str(self.balance)

    def update_wallet_balance(self, transaction_type, amount):
        transaction_type = TransactionType.objects.filter(
            title=transaction_type
        ).first()
        if transaction_type:
            try:
                print("In update wallet")
                with transaction.atomic():
                    if transaction_type.title == CREDIT:
                        self.balance = float(self.balance) + float(amount)
                        self.save()
                    elif transaction_type.title == DEBIT:
                        self.balance = float(self.balance) - float(amount)
                        self.save()
                    wallet_transaction = WalletTransaction.objects.create(
                        **{
                            "wallet": self,
                            "amount": amount,
                            "closing_balance": self.balance,
                            "transaction_type": transaction_type,
                            "status": "SUCCESS",
                        }
                    )
                    wallet_transaction.save()
                    print(wallet_transaction.status)
                    return wallet_transaction
            except Exception as e:
                WalletTransaction.objects.create(
                    **{
                        "wallet": self,
                        "amount": amount,
                        "closing_balance": self.balance,
                        "transaction_type": transaction_type,
                        "status": "FAILED",
                    }
                )
                return e
        else:
            return "transaction_type not found"


class STATUS(models.TextChoices):
    PENDING = "PENDING", ("PENDING")
    SUCCESS = "SUCCESS", ("SUCCESS")
    FAIL = "FAILED", ("FAILED")


class WalletTransaction(TimeStamped):
    transaction_id = models.CharField(max_length=FIFTY)
    status = models.CharField(
        max_length=FIFTY, null=True, choices=STATUS.choices, default=STATUS.PENDING
    )
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=TEN, decimal_places=TWO)
    closing_balance = models.DecimalField(max_digits=TEN, decimal_places=TWO)


@receiver(post_save, sender=WalletTransaction, dispatch_uid="generate_transaction_id")
def set_wallet_txn_id(sender, instance, **kwargs):
    created = kwargs["created"]
    if created:
        instance.transaction_id = generate_wallet_transaction_id(instance.id)
        instance.save()


class Feedback(models.Model):
    order_id = models.ForeignKey("shop.Order", on_delete=models.CASCADE, null=True)
    rating = models.CharField(max_length=SIX, null=True)
    comments = models.TextField(max_length=TWO_HUNDRED, null=True)
    feedback_image = models.ImageField(
        upload_to="feedback", verbose_name="Feedback Image", null=True, blank=True
    )

    def __str__(self):
        return f"Feedback by: {self.order_id.user.name}({self.order_id.user.phone})"


class TenantCategory(TimeStamped):
    name = models.CharField(max_length=HUNDRED)
    description = models.CharField(max_length=HUNDRED)
    is_active = models.BooleanField(default=True)
    logo_url = models.ImageField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tenant Categories"


class TenantUser(AbstractUser):
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True
    )
    role = models.CharField(max_length=TWENTY, choices=ROLE, null=True, blank=True)
    groups = models.ManyToManyField(
        Group, related_name="tenant_users", null=True, blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="tenant_users", null=True, blank=True
    )

    is_verified = models.BooleanField(default=False)
    email = models.EmailField(max_length=FIFTY, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLE, null=True, blank=True)
    username = models.CharField(
        max_length=FIFTY, unique=False, default="", blank=True
    )  # Username can be blank
    name = models.CharField(max_length=HUNDRED, null=True, blank=True)  # Users name

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["name", "username"]

    def __str__(self):
        return self.phone_number

    class Meta:
        __name__ = "Tenant Users"


class Tenant(TimeStamped):
    title = models.CharField(max_length=HUNDRED)
    description = models.TextField()
    custom_domain = models.CharField(
        max_length=HUNDRED, unique=True, blank=True, null=True
    )
    address = models.TextField()
    logo_url = models.ImageField(null=True)
    subdomain = models.CharField(max_length=HUNDRED, unique=True)
    tenant_category = models.ForeignKey(TenantCategory, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    admins = models.ManyToManyField(TenantUser, related_name="tenants", null=True)

    def __str__(self) -> str:
        return self.title


class Subscription(TimeStamped):
    SUB_BILLING_CYCLE = (
        (("1"), "MONTHLY"),
        (("3"), "QUARTER"),
        (("6"), "HALF-YEARLY"),
        (("C"), "YEARLY"),
    )
    name = models.CharField(max_length=TWENTY)
    description = models.TextField(max_length=HUNDRED)
    price = models.DecimalField(max_digits=8, decimal_places=TWO)
    is_active = models.BooleanField(default=True)
    billing_cycle = models.CharField(max_length=TWENTY, choices=SUB_BILLING_CYCLE)

    def __str__(self) -> str:
        return self.name

    def calculate_expiry_date(self):
        # Get the current time
        now = timezone.now()
        # Set the expiry date based on the billing cycle
        if self.billing_cycle == "1":
            # Monthly
            expiry_date = now + timedelta(days=30)
        elif self.billing_cycle == "3":
            # Quarterly
            expiry_date = now + timedelta(days=90)
        elif self.billing_cycle == "6":
            # Half-yearly
            expiry_date = now + timedelta(days=180)
        elif self.billing_cycle == "C":
            # Yearly
            expiry_date = now + timedelta(days=365)
        # Return the expiry date
        return expiry_date


class SubscriptionDetail(TimeStamped):
    SUB_STATUS_CHOICE = ((("A"), "ACTIVE"), (("C"), "CANCELLED"), (("E"), "EXPIRED"))
    tenant_id = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    subscription_id = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=TWENTY, choices=SUB_STATUS_CHOICE)
    payment = models.ForeignKey("shop.Payment", on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return f"{str( self.tenant_id )} -> {str( self.start_date )}"
