from django.contrib import admin
from .models import *
from .forms import ProfileForm
from django.contrib.auth.admin import UserAdmin


class ProfileAdmin(UserAdmin):
    model = Profile
    add_form = ProfileForm
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            "UserDetails",
            {
                "fields": (
                    "name",
                    "phone_number",
                    "staff_category",
                    "is_verified",
                    "role",
                    "inventory",
                    "device_id",
                    "attributes",
                )
            },
        ),
    )
    list_filter = ("is_verified",)
    list_display = ("__str__",)
    search_fields = ("phone_number", "name")


class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ("title",)


class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "max_balance", "is_active")


class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "wallet",
        "transaction_id",
        "status",
        "transaction_type",
        "amount",
        "closing_balance",
    )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Staff)
admin.site.register(OTP)
admin.site.register(Feedback)
admin.site.register(TransactionType, TransactionTypeAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(WalletTransaction, WalletTransactionAdmin)

# Tenants
admin.site.register(Tenant)
admin.site.register(TenantCategory)
admin.site.register(TenantUser)
admin.site.register(Subscription)
admin.site.register(SubscriptionDetail)
