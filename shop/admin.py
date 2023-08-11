from django.contrib import admin
from .models import *
from django.http import HttpResponse
import csv, datetime
from django.contrib.admin.filters import SimpleListFilter
from django import forms
from phurti.models import *


class StockAdminInline(admin.TabularInline):
    model = Stock


class OrderItemAdminInline(admin.TabularInline):
    model = OrderItem
    fields = (
        "get_title",
        "product_address",
        "description",
        "quantity_remaining",
        "quantity",
        "price",
        "discount_code",
        "final_price",
        "expiry",
        "batch_number",
    )
    readonly_fields = [field.name for field in OrderItem._meta.fields] + [
        "get_title",
        "quantity_remaining",
        "product_address",
    ]

    def get_title(self, obj):
        return str(obj.title) + " × " + str(obj.quantity)

    def quantity_remaining(self, obj):
        if obj.order_id and obj.product_id:
            si = SellableInventory.objects.filter(
                inventory_id=obj.order_id.inventory_id, product_id=obj.product_id_id
            ).first()
            if si:
                return si.quantity_remaining
            else:
                return "NOT LISTED"
        else:
            return "NOT FOUND"

    def product_address(self, obj):
        if obj.order_id and obj.product_id:
            si = SellableInventory.objects.filter(
                inventory_id=obj.order_id.inventory_id, product_id=obj.product_id_id
            ).first()
            if si:
                return si.address
            else:
                return "NA"
        else:
            return "NA"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class InvoiceAdminInline(admin.TabularInline):
    model = Invoice
    readonly_fields = [
        field.name for field in Invoice._meta.fields if field.name != "invoice_url"
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


# Invoice
class InventoryAdmin(admin.ModelAdmin):
    # inlines = [
    #     StockAdminInline,
    # ]
    list_display = ("__str__", "is_active")


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [
        InvoiceItemInline,
    ]
    readonly_fields = ["invoice_id"]

    list_display = ("__str__", "final_price", "invoice_url")


class StockAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "created_on",
        "updated_on",
        "procurement_price_per_product",
        "inventory",
        "user",
        "quantity",
    )
    search_fields = ["product__product_name", "user__phone_number"]
    date_hierarchy = "created_on"


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemAdminInline]
    list_display = (
        "__str__",
        "source",
        "inventory",
        "customer",
        "payment_status",
        "status",
        "total_price",
        "prescription_url",
    )
    list_filter = ("fulfilment_type", "source", "inventory", "status")
    exclude = ("delivery_type", "delivery_address")
    date_hierarchy = "created_on"
    search_fields = ["customer__phone_number", "customer__name"]
    # readonly_fields = ['customer', 'cart', 'delivery_type', 'source', 'status', 'inventory', 'total_price']

    def save_model(self, request, instance, form, change):
        user = request.user
        instance = form.save(commit=False)
        # if not change or not instance.delivered_by:
        #     instance.delivered_by = user
        # instance.save()
        form.save_m2m()
        return instance


class SaltAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "created_on",
        "updated_on",
        "title",
        "description",
        "is_active",
    )


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_on", "updated_on", "name", "is_active")


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "unit",
        "description",
        "sku",
        "created_on",
        "is_active_product",
    ]
    # list_select_related = ['category']
    exclude = ["barcode", "category", "price", "market_price"]
    list_filter = [
        "created_on",
        "updated_on",
        "is_active_product",
        "is_active_description",
        "category",
    ]
    search_fields = ["product_name", "price"]
    readonly_fields = ["sku"]


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "created_on",
        "updated_on",
        "is_active",
        "quantity",
        "time_slot",
    )
    autocomplete_fields = ["products", "customer", "new_customer"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "priority", "active")
    autocomplete_fields = ["products"]


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ["order"]


class ChannelAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "name",
        "phone_number",
        "license_number",
        "gst_number",
        "address",
        "is_active",
    )


admin.site.register(Channel, ChannelAdmin)
admin.site.register(User)
admin.site.register(HsnCodes)
admin.site.register(Salt, SaltAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(DeliveryType)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem)
admin.site.register(StockUnit)


@admin.register(WastedProduct)
class WastedProductCustom(admin.ModelAdmin):
    list_display = [
        "__str__",
        "added_by",
        "created_on",
        "updated_on",
        "product",
        "quantity",
        "quantity_units",
        "reason",
    ]
    date_hierarchy = "created_on"


@admin.register(DailyInventoryTracker)
class DailyInventoryTrackerCustom(admin.ModelAdmin):
    list_display = [
        "__str__",
        "created_on",
        "updated_on",
        "inventory_id",
        "quantity_remaining",
    ]
    date_hierarchy = "created_on"


@admin.register(OrderScheduler)
class OrderSchedulerCustom(admin.ModelAdmin):
    list_display = [
        "schedule_time",
        "created_on",
        "updated_on",
        "order_id",
        "is_active",
    ]
    date_hierarchy = "created_on"


@admin.register(OrderItem)
class OrderItemCustom(admin.ModelAdmin):
    list_display = ["product_id", "quantity", "price", "final_price", "discount_code"]


@admin.register(FavouriteProduct)
class FavouriteProductCustom(admin.ModelAdmin):
    list_display = ["product_id", "user_id"]


class DiscountAttributesAdminInline(admin.TabularInline):
    model = DiscountAttributes
    max_num = 1
    min_num = 1

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return True

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(~Q(products=None))
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Discount)
class DiscountCustom(admin.ModelAdmin):
    inlines = [DiscountAttributesAdminInline]
    readonly_fields = ["start_time"]
    list_display = [
        "code",
        "value",
        "start_time",
        "end_time",
        "discount_code_type",
        "is_active",
        "is_applied",
    ]


@admin.register(Offers)
class OffersCustom(admin.ModelAdmin):
    list_display = [
        "title",
        "desktop_view_image",
        "tablet_view_image",
        "mobile_view_image",
        "action_link",
    ]


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment;" "filename={}.csv".format(
        opts.verbose_name
    )
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)

    return response


export_to_csv.short_description = "Export to CSV"  # short description


class ProductAddressFilter(SimpleListFilter):
    title = "Shelf Number"
    parameter_name = "shelf_number"

    def lookups(self, request, model_admin):
        shelves = set()
        for sellable_inventory_obj in model_admin.model.objects.all():
            if sellable_inventory_obj.address:
                shelves.add(int(sellable_inventory_obj.address.split("-")[0]))
        return [("Unmapped", "Unmapped")] + [
            (shelf, str(shelf)) for shelf in sorted(shelves)
        ]

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "Unmapped":
                return queryset.filter(address__isnull=True)
            return queryset.filter(address__startswith=self.value() + "-").order_by(
                "address"
            )
        return queryset


class ProductAddressFilter(SimpleListFilter):
    title = "Shelf Number"
    parameter_name = "shelf_number"

    def lookups(self, request, model_admin):
        shelves = set()
        for sellable_inventory_obj in model_admin.model.objects.all():
            if sellable_inventory_obj.address:
                shelves.add(int(sellable_inventory_obj.address.split("-")[0]))
        return [("Unmapped", "Unmapped")] + [
            (str(shelf), str(shelf)) for shelf in sorted(shelves)
        ]

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "Unmapped":
                return queryset.filter(address__isnull=True)
            return queryset.filter(address__startswith=self.value() + "-").order_by(
                "address"
            )
        return queryset


class ProductPriceVariationForm(forms.ModelForm):
    class Meta:
        model = ProductPriceVariation
        fields = "__all__"

    @staticmethod
    def has_delete_permission():
        return False

    def clean(self):
        sellable_inventory = self.cleaned_data.get("sellable_inventory")
        start_date = self.cleaned_data.get("valid_from")
        end_date = self.cleaned_data.get("valid_to")
        instance = self.cleaned_data.get("id")
        if start_date is None:
            raise forms.ValidationError("Start date cannot be empty")
        elif end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be greater then  end date.")
        elif start_date:
            if instance:
                prev_variation = ProductPriceVariation.objects.filter(
                    sellable_inventory=sellable_inventory, id__lt=instance.id
                ).last()
            else:
                prev_variation = ProductPriceVariation.objects.filter(
                    sellable_inventory=sellable_inventory
                ).last()
            if prev_variation:
                if prev_variation.valid_to is None:
                    raise forms.ValidationError(
                        "There is no end date defined in previous price variation. Cannot proceed"
                        " without expiring the last one"
                    )
                elif prev_variation.valid_to and start_date < prev_variation.valid_to:
                    raise forms.ValidationError(
                        "Overlapping start date with end date of previous price variation. Cannot"
                        " proceed"
                    )
        return self.cleaned_data


class ProductPriceVariationAdminInline(admin.TabularInline):
    model = ProductPriceVariation
    form = ProductPriceVariationForm
    extra = 1

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SellableInventory)
class SellableInventoryCustom(admin.ModelAdmin):
    inlines = [ProductPriceVariationAdminInline]
    list_display = [
        "inventory",
        "product",
        "product_description",
        "categories",
        "quantity_remaining",
        "address",
        "expiry",
        "batch_number",
    ]
    list_filter = ("inventory__name", ProductAddressFilter)
    search_fields = ["product__product_name"]
    actions = [export_to_csv]

    def product_description(self, obj):
        product = Product.objects.get(id=obj.product_id)
        return str(product.description)

    def categories(self, obj):
        product = Product.objects.get(id=obj.product_id)
        if product:
            categories = product.categories.all()
            if categories:
                parents = []
                for category in categories:
                    parents.append(category.name)
                return parents
            else:
                return "NOT LISTED"
        else:
            return "NOT LISTED"

admin.site.register(VariationTypes)
admin.site.register(VariationCombos)
admin.site.register(VariationOptions)
admin.site.register(ProductVariation)
admin.site.register(Toppings)
