from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ("__str__", "is_active", "email")
    search_fields = ("name", "phone", "email")


admin.site.register(Customer, CustomerAdmin)


@admin.register(Alternative)
class AlternativeCustom(admin.ModelAdmin):
    list_display = ["customer", "type", "value"]
