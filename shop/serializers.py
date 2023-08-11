from random import choices
from django.db.models import fields
from rest_framework import serializers
from .models import *
from account.models import Profile
from customer.models import Customer
from contactus.models import *
from django.db.models import F
from phurti.models import *


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    sub_categories = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_image(self, obj):
        return obj.get_image_url()

    def get_sub_categories(self, obj):
        category = Category.objects.filter(parent=obj, active=True).order_by(
            F("priority").asc(nulls_last=True)
        )
        if category:
            return CategorySerializer(category, many=True).data
        return []

    def get_category(self, obj):
        if obj.parent:
            return obj.name

class MiniCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["id","name"]

   

    def get_category(self, obj):
        if obj.parent:
            return obj.name
         
class ProductCategorySerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    market_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "photo",
            "market_price",
            "price",
            "sku",
            "is_active_product",
            "barcode",
            "description",
        ]

    def get_photo(self, obj):
        return obj.get_photo_url()

    def get_market_price(self, obj):
        request = self.context.get("request", None)
        if request:
            user = request.user
            if user:
                price_variation = obj.current_price_variation(user.inventory_id)
                if price_variation:
                    return price_variation.market_price
        return obj.market_price

    def get_price(self, obj):
        request = self.context.get("request", None)
        if request:
            user = request.user
            if user:
                price_variation = obj.current_price_variation(user.inventory_id)
                if price_variation:
                    return price_variation.price
        return obj.price



class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    market_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "category",
            "photo",
            "market_price",
            "price",
            "sku",
            "is_active_product",
            "barcode",
            "description",
        ]

    def get_category(self, obj):
        if obj.category:
            return {
                "name": obj.category.name,
                "description": obj.category.description,
                "slug": obj.category.slug,
            }
        return {}

    def get_photo(self, obj):
        return obj.get_photo_url()

    def get_market_price(self, obj):
        request = self.context.get("request", None)
        if request:
            user = request.user
            if user:
                price_variation = obj.current_price_variation(user.inventory_id)
                if price_variation:
                    return price_variation.market_price
        return obj.market_price

    def get_price(self, obj):
        request = self.context.get("request", None)
        if request:
            user = request.user
            if user:
                price_variation = obj.current_price_variation(user.inventory_id)
                if price_variation:
                    return price_variation.price
        return obj.price

class MiniProductSerializer(serializers.ModelSerializer):
    category = serializers.ListField(required=False, allow_empty=True)

    class Meta:
        model = Product
        fields = [
            "product_name",
            "is_active_product",
            "price",
            "market_price",
            "category",
            "description",
            "is_active_description",
            "sku",
            "photo",
            # "out_of_stock",
            "barcode",
            "category",
            "tenant",
        ]
        extra_kwargs = {
            "product_name": {"required": False}
        }

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["id", "name", "address", "code", "pincode", "is_active"]


class SellableInventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    inventory = InventorySerializer()

    class Meta:
        model = SellableInventory
        fields = [
            "id",
            "is_active",
            "quantity_remaining",
            "address",
            "expiry",
            "batch_number",
            "tenant",
            "inventory",
            "product",
            "quantity_remaining",
        ]


class HelpingSerializer(serializers.Serializer):
    product = serializers.CharField(max_length=400)
    quantity = serializers.CharField(max_length=400)


class CartItemSerializer(serializers.Serializer):
    items = HelpingSerializer(many=True)


class CartItemOneSerializer(serializers.Serializer):
    product = serializers.CharField(max_length=400)
    quantity = serializers.CharField(max_length=400)


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class ThumbnailImageSerializer(serializers.Serializer):
    url = serializers.CharField(allow_null=True, allow_blank=True)
    height = serializers.IntegerField(allow_null=True)
    width = serializers.IntegerField(allow_null=True)


class StateBodySerializer(serializers.Serializer):
    value = serializers.CharField()
    media_width = serializers.IntegerField(allow_null=True)
    media_height = serializers.IntegerField(allow_null=True)
    thumbnail_image = ThumbnailImageSerializer()


class StateSerializer(serializers.Serializer):
    media = serializers.FileField(allow_null=True, required=False)
    action = serializers.CharField()
    state_type = serializers.CharField()
    body = serializers.JSONField()
    sender = serializers.CharField()
    created_on = serializers.CharField()

    def validate_media(self, value):
        if value.content_type not in [
            "application/pdf",
            "image/png",
            "image/jpg",
            "image/jpeg",
            "image/gif",
        ]:
            raise serializers.ValidationError("Unsupported file format")
        if value.size > 10485760:
            raise serializers.ValidationError(
                "File too large, please upload file of size less than 10Mb"
            )
        return value


class PrescriptionUploadSerializer(serializers.Serializer):
    media = serializers.FileField()
    action = serializers.CharField()
    state_type = serializers.CharField()
    body = serializers.JSONField()
    sender = serializers.CharField()
    created_on = serializers.CharField()

    def validate_media(self, value):
        if value.content_type not in [
            "application/pdf",
            "image/png",
            "image/jpg",
            "image/jpeg",
            "image/gif",
        ]:
            raise serializers.ValidationError("Unsupported file format")
        if value.size > 10485760:
            raise serializers.ValidationError(
                "File too large, please upload file of size less than 10Mb"
            )
        return value


class RequestCallbackSerializer(serializers.ModelSerializer):
    action = serializers.CharField(required=True)

    class Meta:
        model = CallbackRequest
        fields = "__all__"


class OrderSerializerAll(serializers.ModelSerializer):
    invoice_url = serializers.SerializerMethodField()
    cart = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    # delivered_by = serializers.SerializerMethodField()
    delivery_type = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    def get_cart(self, obj):
        orderitem = OrderItem.objects.filter(order_id=obj.id)
        serializer = OrderItemSerializer(orderitem, many=True)
        return serializer.data

    def get_user(self, obj):
        return {"name": obj.customer.name, "phone": obj.customer.phone_number}

    def get_invoice_url(self, obj):
        invoice = Invoice.objects.get(order_id=obj.id)
        if invoice:
            return invoice.invoice_url
        else:
            return ""

    # def get_delivered_by(self, obj):
    #     if obj.delivered_by:
    #         return obj.delivered_by.username

    def get_delivery_type(self, obj):
        if obj.delivery_type:
            return obj.delivery_type


class OrderItemSerializer(serializers.ModelSerializer):
    discount_code = serializers.SerializerMethodField(allow_null=True, required=False)
    description = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField(allow_null=True, required=False)
    product_address = serializers.SerializerMethodField(allow_null=True, required=False)
    hsn_codes = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = "__all__"

    def get_hsn_codes(self, obj):
        hsn_codes = []
        if obj.product_id:
            for hsn_code in obj.product_id.hsn_codes.all():
                hsn_codes.append(str(hsn_code.code))

        return ", ".join(hsn_codes)

    def get_description(self, obj):
        if obj.product_id:
            if obj.product_id.is_active_description:
                return obj.description
            else:
                return ""
        else:
            return obj.description

    def get_photo(self, obj):
        if obj.product_id:
            return obj.product_id.get_photo_url()

    def get_product_address(self, obj):
        if obj.product_id:
            si = SellableInventory.objects.filter(
                inventory=obj.order_id.inventory, product=obj.product_id
            ).first()
            if si:
                return si.address
        return "N/A"

    def get_discount_code(self, obj):
        if obj.discount_code:
            temp_data = {
                "code": obj.discount_code.code,
                "value": obj.discount_code.value,
                "is_active": obj.discount_code.is_active,
            }
            return temp_data
        return {}


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class HelpingEverythinOrderSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=400)
    product_description = serializers.CharField(
        max_length=400, allow_blank=True, allow_null=True
    )
    product_price = serializers.CharField(max_length=400)
    product_quantity = serializers.CharField(max_length=400)
    product_unit = serializers.CharField(
        max_length=400, allow_blank=True, allow_null=True
    )
    product_id = serializers.CharField(
        max_length=400, allow_blank=True, allow_null=True
    )
    product_expiry = serializers.CharField(max_length=HUNDRED)
    product_batch_number = serializers.CharField(max_length=HUNDRED)


class EverythinOrderSerializer(serializers.Serializer):
    items = HelpingEverythinOrderSerializer(many=True)
    name = serializers.CharField(max_length=200)
    address = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=200)
    delivery_charge = serializers.CharField(max_length=200)
    packaging_charge = serializers.CharField(max_length=200)
    schedule_time = serializers.CharField(max_length=400, allow_blank=True)
    inventory = serializers.CharField(max_length=400, allow_blank=True)


class ProductMiniSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="product_name")
    description = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    remaining_products = serializers.SerializerMethodField()
    price_variation = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_description(self, obj):
        if obj.is_active_description:
            return obj.description
        else:
            return ""

    def get_photo(self, obj):
        return obj.get_photo_url()

    def get_category(self, obj):
        category = Category.objects.filter(products=obj)
        if category:
            final_category = []
            for category_item in category:
                final_category.append(category_item.name)
            return final_category

        return []

    def get_remaining_products(self, obj):
        sellable_inventory = SellableInventory.objects.filter(product=obj)
        data = []
        for product in sellable_inventory:
            product_remaining = {
                "inventory_id": product.inventory.id,
                "product_remaining": product.quantity_remaining,
                "address": product.address,
            }
            data.append(product_remaining)
        return data

    def get_price_variation(self, obj):
        inv = Inventory.objects.all()
        price_variation_data = []
        for inventory in inv:
            price_variation = obj.current_price_variation(inventory.id)
            if price_variation:
                price_values = {
                    "market_price": price_variation.market_price,
                    "inventory_id": inventory.id,
                    "price": price_variation.price,
                }
                price_variation_data.append(price_values)

        return price_variation_data


class InvoiceItemeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["title", "price", "description"]


class ProductStockSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["product_name", "id", "description"]

    def get_description(self, obj):
        if obj.is_active_description:
            return obj.description
        else:
            return ""


class StockUnitSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="unit")

    class Meta:
        model = StockUnit
        fields = ["id", "name"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "phone_number"]


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="phone")

    class Meta:
        model = User
        fields = ["id", "name", "phone_number"]


class StockSerializer(serializers.Serializer):
    added_by = serializers.CharField(max_length=200)
    stock_quantity = serializers.DecimalField(max_digits=20, decimal_places=FOUR)
    stock_unit = serializers.CharField(
        max_length=200, allow_null=True, allow_blank=True
    )
    stock_product = serializers.CharField(max_length=200)
    procurement_price_per_product = serializers.CharField(
        max_length=200, allow_blank=True
    )
    inventory = serializers.CharField(max_length=200)


class CreateStockSerializer(serializers.Serializer):
    data = StockSerializer(many=True)


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ("id", "name")


# helpers for wasted product serializer
class HelpWastedProductSerializer(serializers.Serializer):
    added_by = serializers.CharField(max_length=200)
    stock_product = serializers.CharField(max_length=200)
    stock_quantity = serializers.DecimalField(max_digits=20, decimal_places=2)
    stock_unit = serializers.CharField(max_length=200)
    reason = serializers.CharField(max_length=200)
    wasted_product_image = serializers.CharField()


# for wasted product post api
class WastedProductSerializer(serializers.Serializer):
    data = HelpWastedProductSerializer(many=True)
    # class Meta:
    #     model = WastedProduct
    #     fields = '__all__'


# for stock post api
class StockUnitFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockUnit
        fields = "__all__"


# for inventory post api
class InventoryFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"


class ProductFullSerializer(serializers.ModelSerializer):
    category = serializers.ListField(required=False, allow_empty=True)

    class Meta:
        model = Product
        fields = [
            "product_name",
            "is_active_product",
            "price",
            "market_price",
            "category",
            "description",
            "is_active_description",
            "sku",
            "photo",
            # "out_of_stock",
            "barcode",
            "category",
            "tenant",
        ]


class FavouriteProductSerializer(serializers.ModelSerializer):
    product_id = ProductSerializer()

    class Meta:
        model = FavouriteProduct
        fields = "__all__"


class FavouriteProductSerializerMin(serializers.ModelSerializer):
    class Meta:
        model = FavouriteProduct
        fields = ["product_id"]


# Recent Order serializer for checking users latest order.
class RecentOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    cust_name = serializers.SerializerMethodField()
    cust_phone = serializers.SerializerMethodField()
    delivery_executive_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    def get_items(self, obj):
        orderitem = OrderItem.objects.filter(order_id=obj.id)
        serializer = OrderItemSerializer(orderitem, many=True)
        return serializer.data

    def get_cust_name(self, obj):
        if obj.customer:
            return obj.customer.name
        return ""

    def get_cust_phone(self, obj):
        if obj.customer:
            return obj.customer.phone_number
        return ""

    def get_delivery_executive_name(self, obj):
        if obj.delivered_by:
            return obj.delivered_by.name
        return ""


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = "__all__"


class CartDiscountSerializer(serializers.Serializer):
    discount_code = serializers.CharField(max_length=400)


class OffersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offers
        fields = "__all__"


class HSNCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HsnCodes
        fields = "__all__"


class GETStocksSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer()
    product = ProductSerializer()
    units = StockUnitSerializer()

    class Meta:
        model = Stock
        fields = "__all__"


class StocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class SellableInventoriesSerializer(serializers.ModelSerializer):
    id = models.IntegerField()
    class Meta:
        model = SellableInventory
        fields = ("tenant", "inventory", "product", "quantity_remaining")


class DashboardOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "tenant", "status")