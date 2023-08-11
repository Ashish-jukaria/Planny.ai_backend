from django.db.models.deletion import CASCADE

import phurti.models
import account.models
from phurti.models import TimeStamped
from django.db import models
from django.core.validators import RegexValidator
from django.utils.timezone import localtime
from account.models import Profile
from django.utils.text import slugify
from django.utils.timezone import now
from .constants import *
from decimal import Decimal
from customer.models import Customer
import datetime
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.db.models import Q, JSONField
from decimal import Decimal
from scripts.put_detail import create_cache  # Importing cache function
from django.db import transaction
from dateutil.tz import tzlocal
from shop.utils import get_discounted_amount_cart
from shop.configs import *
import logging
from shop.configs import DEFAULT_ORDER_STATE
from shop.enums import *
from account.models import Tenant

logger = logging.getLogger("phurti")


class Userquery(models.QuerySet):
    def search(self, query):
        lookup = (
            Q(name__iexact=query)
            | Q(name__icontains=query)
            | Q(phone__iexact=query)
            | Q(phone__icontains=query)
        )

        return self.filter(lookup)


class UserManager(models.Manager):
    def get_queryset(self):
        return Userquery(self.model, using=self._db)

    def search(self, query=None):
        if query is None:
            return self.get_queryset().none()
        return self.get_queryset().search(query)


class Productquery(models.QuerySet):
    def search(self, query):
        lookup = Q(product_name__iexact=query) | Q(product_name__icontains=query)

        return self.filter(lookup)


class ProductManager(models.Manager):
    def get_queryset(self):
        return Productquery(self.model, using=self._db)

    def search(self, query=None):
        if query is None:
            return self.get_queryset().none()
        return self.get_queryset().search(query)


class InvoiceItemquery(models.QuerySet):
    def search(self, query):
        lookup = Q(title__iexact=query) | Q(title__icontains=query)

        return self.filter(lookup)


class InvoiceItemManager(models.Manager):
    def get_queryset(self):
        return InvoiceItemquery(self.model, using=self._db)

    def search(self, query=None):
        if query is None:
            return self.get_queryset().none()
        return self.get_queryset().search(query)


class Inventory(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, default=1)
    name = models.CharField(max_length=HUNDRED)
    address = models.TextField()
    code = models.CharField(max_length=FIFTY)
    pincode = models.CharField(max_length=TEN, null=True, blank=True)
    longitude = models.CharField(max_length=FIFTY, null=True, blank=True)
    latitude = models.CharField(max_length=FIFTY, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} :{self.code}"


class CodeField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(CodeField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).upper()


class Discount(TimeStamped):  # For product discount on order.
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, default=1)
    start_time = models.DateTimeField(auto_now_add=True)  # Code start date
    end_time = models.DateTimeField(blank=True, null=True)  # code end date
    discount_code_type = models.CharField(
        choices=CODE_TYPE, max_length=FIFTY
    )  # code discount type.
    value = models.DecimalField(
        max_digits=TWENTY,
        decimal_places=FOUR,
    )  # Code Value like price 20
    maximum_discount = models.IntegerField(default=ZERO)
    code = CodeField(max_length=FIFTY, null=True, unique=True)  # code name PHURTI100
    code_description = models.CharField(
        max_length=HUNDRED, blank=True, null=True
    )  # Discription of the discount code to apply.
    is_active = models.BooleanField(default=True)  # code is active?
    minimum_order_value = models.IntegerField(
        default=ONE
    )  # Minimum order value to apply coupon
    is_applied = models.BooleanField(
        default=False
    )  # if one_time_per_user true and customer applied the coupon then it will be true
    apply_type = models.CharField(
        max_length=HUNDRED, choices=APPLY_TYPE_CHOICES, default="cart"
    )

    def __str__(self):
        return f"{self.code}-->{self.discount_code_type}"

    @property
    def is_valid(self):
        time_to_check = datetime.datetime.now(tzlocal())
        if self.is_active:
            if self.end_time:
                return self.end_time > time_to_check >= self.start_time
            return time_to_check >= self.start_time
        return False

    def apply_discount(self, cart, data={}):
        try:
            with transaction.atomic():
                discount = self
                discounted_price = 0  # this is the price to divide equally on products
                # if cart:
                count_items = cart.cartitem.all().count()
                applied_on = data.get("applied_on")
                apply_type = data.get("apply_type")
                cartitems = cart.cartitem.all()
                if "filtered_data" in data:
                    data["filtered_data"] = data.get("filtered_data").distinct()
                if apply_type == ITEMS:
                    if applied_on and data.get("filtered_data"):
                        cartitems = data.get("filtered_data")
                        count_items = cartitems.count()
                    total_price_user = cart.get_total_price(
                        cartitems=cartitems
                    )  # Total price user ordered
                    total_item_discounted_price = 0
                    if (
                        discount.discount_code_type == "A"
                    ):  # for subtracting discount for Absoulute value
                        discount_amount = discounted_price = discount.value
                        if discount.maximum_discount < discount_amount:
                            discount_amount = (
                                discounted_price
                            ) = discount.maximum_discount
                        total_price_user -= discount_amount
                    elif discount.discount_code_type == "P":
                        discount_amount = discounted_price = (
                            total_price_user * discount.value
                        ) / 100
                        if discount.maximum_discount < discount_amount:
                            discount_amount = (
                                discounted_price
                            ) = discount.maximum_discount
                        total_price_user -= discount_amount
                        total_item_discounted_price = discount_amount
                    # if cart and cart.cartitem:
                    remove_value_per_item = Decimal(discounted_price / count_items)
                    for cartitem in cartitems:
                        if apply_type == ITEMS:
                            if discount.discount_code_type == "P":
                                total_price_user = cart.get_total_price(
                                    cartitems=cartitems.filter(id=cartitem.id)
                                )
                                discount_amount = discounted_price = (
                                    total_price_user * discount.value
                                ) / 100
                                if discount.maximum_discount < discount_amount:
                                    discount_amount = (
                                        discounted_price
                                    ) = discount.maximum_discount
                                total_price_user -= discount_amount
                                remove_value_per_item = discounted_price
                            if discount.discount_code_type == "A":
                                remove_value_per_item = (
                                    discounted_price * cartitem.quantity
                                )
                        cartitem_total_price = cartitem.get_total_cartitem_price()
                        temp_final_price = (
                            cartitem_total_price - remove_value_per_item
                        )  # percentage discount substraction
                        if cartitem_total_price < remove_value_per_item:
                            price_diff = remove_value_per_item - cartitem_total_price
                            temp_final_price = cartitem_total_price - price_diff
                            remove_value_per_item += price_diff
                        cartitem.final_price = temp_final_price
                        cartitem.discount_code = discount
                        cartitem.save()
                    cart.refresh_from_db()
                    cart.total_price = (
                        cart.get_total_price(cartitems=cart.cartitem.all())
                        - total_item_discounted_price
                    )
                    cart.save(update_fields=["total_price"])
                else:
                    discounted_price = get_discounted_amount_cart(discount, cart, data)
                    cart.total_price = cart.get_total_unit_price() - discounted_price
                    cart.cartitem.update(discount_code=discount)
                    cart.save(update_fields=["total_price"])
            return True
        except Exception as err:
            return False


class DiscountAttributes(models.Model):
    discount = models.ForeignKey(
        Discount, related_name="discount_attributes", on_delete=models.CASCADE
    )
    applied_on = models.CharField(max_length=HUNDRED, choices=APPLIED_CHOICES)
    category = models.ManyToManyField(
        "Category", related_name="category_discounts", blank=True
    )
    inventory = models.ManyToManyField(
        Inventory, related_name="inventory_discounts", blank=True
    )
    product = models.ManyToManyField(
        "Product", related_name="product_discounts", blank=True
    )
    first_order_per_user = models.BooleanField(default=False)
    one_time_per_user = models.BooleanField(default=False)
    customer = models.ManyToManyField(
        Profile, verbose_name="customer_discounts", blank=True
    )
    attribute_type = models.CharField(
        max_length=HUNDRED, choices=ATTRIBUTE_CHOICES, default="transactional"
    )


class StockUnit(TimeStamped):
    unit = models.CharField(max_length=FIFTY, blank=True, null=True)
    unit_description = models.CharField(max_length=FIFTY, blank=True, null=True)

    def __str__(self):
        return f"{self.unit}"


class Stock(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, default=1)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Added by")
    quantity = models.DecimalField(
        default=0.0,
        verbose_name="stock quantity",
        max_digits=TWENTY,
        decimal_places=FOUR,
    )
    units = models.ForeignKey(
        StockUnit, on_delete=models.CASCADE, verbose_name="stock units", null=True
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, verbose_name="stock_product"
    )
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        verbose_name="Inventory",
        null=True,
        blank=False,
    )
    procurement_price_per_product = models.CharField(max_length=FIFTY, null=True)
    expiry = models.DateField(null=True)
    batch_number = models.CharField(max_length=HUNDRED, null=True)
    purchase_trade_rate = models.DecimalField(
        default=0.0, max_digits=TWENTY, decimal_places=FOUR
    )
    net_rate = models.DecimalField(default=0.0, max_digits=TWENTY, decimal_places=FOUR)
    discount = models.DecimalField(default=0.0, max_digits=TWENTY, decimal_places=FOUR)
    gst = models.DecimalField(default=0.0, max_digits=TWENTY, decimal_places=FOUR)
    packaging = models.CharField(null=True, blank=True, max_length=HUNDRED)

    def __str__(self):
        return f"{self.product}: {self.quantity}"


@receiver(
    pre_delete,
    sender=Stock,
    dispatch_uid="Update Sallable Inventory Product if stock deleted",
)
def update_sellableinventory_product_stock(sender, instance, **kwargs):
    if instance.inventory:
        recaptured_stock = SellableInventory.objects.filter(
            inventory=instance.inventory,
            product=instance.product,
            expiry=instance.expiry,
            # batch_number=instance.batch_number,
        )
        if recaptured_stock:
            recaptured_stock = recaptured_stock.first()
            if instance.quantity > 0:
                recaptured_stock.quantity_remaining -= float(instance.quantity)
                recaptured_stock.save()
            else:
                recaptured_stock.quantity_remaining = 0
                recaptured_stock.save()


@receiver(post_save,sender=Stock,)
def create_sellableinventory(sender, instance, **kwargs):
    sellableinventory = SellableInventory.objects.filter(
        tenant = instance.tenant,
        inventory = instance.inventory,
        product = instance.product,   
        ).first()
    
    # For PUT Request of stock
    if sellableinventory:
        sellableinventory.product = instance.product
        sellableinventory.quantity_remaining = instance.quantity

        sellableinventory.save()      

    # For POST Request of stock
    elif instance.inventory:
        SellableInventory.objects.create(
            tenant = instance.tenant,
            inventory = instance.inventory,
            product = instance.product,
            quantity_remaining = instance.quantity,            
        )


class User(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, default=1)
    name = models.CharField(max_length=FIFTY, blank=False)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{10,15}$",
        message="Phone number must be entered in the format: '987654321'. Up to 15 digits allowed.",
    )
    phone = models.CharField(validators=[phone_regex], max_length=TWENTY)
    objects = UserManager()

    def __str__(self):
        return f"{self.name} :{self.phone}"


class Category(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=FIFTY, verbose_name="category-name")
    description = models.TextField(max_length=TWO_HUNDRED, blank=True)
    slug = models.SlugField(max_length=FIFTY, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to="category", verbose_name="Category Image", null=True, blank=True
    )
    colour = models.CharField(null=True, blank=True, max_length=TWENTY)
    home_page = models.BooleanField(
        verbose_name="Show this category on home page", default=False
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="sub_categories",
        default=None,
    )
    products = models.ManyToManyField("Product", related_name="categories", blank=True)
    tenant = models.ForeignKey(
        account.models.Tenant, on_delete=models.CASCADE, default=1
    )

    class Meta:
        unique_together = ("slug", "parent")
        verbose_name_plural = "categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return " -> ".join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super(Category, self).save(*args, **kwargs)

    def get_image_url(self):
        return f"https://cdn.phurti.in/phurti-cloudfront/{self.image}"

    @property
    def is_leaf_category(self):
        child_categories = Category.objects.filter(parent_id=self.id)
        if child_categories:
            return False
        return True


class HsnCodes(TimeStamped):
    code = models.CharField(max_length=EIGHT, default=None)
    description = models.CharField(max_length=ONE_THOUSAND, null=True, blank=True)
    gst = models.DecimalField(
        max_digits=FOUR, decimal_places=TWO, null=True, blank=True
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Salt(TimeStamped):
    title = models.CharField(max_length=HUNDRED)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Manufacturer(TimeStamped):
    name = models.CharField(max_length=TWO_HUNDRED)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=1)
    product_name = models.CharField(max_length=HUNDRED)
    is_active_product = models.BooleanField(
        default=True, verbose_name="Activate Product"
    )
    price = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, null=True, blank=True
    )  # Our selling price
    market_price = models.DecimalField(
        verbose_name="Market Price",
        max_digits=TWENTY,
        decimal_places=FOUR,
        null=True,
        blank=True,
    )  # Market price for strikethrough
    category = models.ForeignKey(Category, on_delete=CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active_description = models.BooleanField(
        default=True, verbose_name="Activate Description"
    )
    sku = models.CharField(max_length=HUNDRED, blank=True, null=True)
    photo = models.ImageField(
        upload_to="products",
        verbose_name="Photo",
        null=True,
        default="products/phurti_hiEVV4u.PNG",
    )
    barcode = models.CharField(max_length=FIFTY, null=True, blank=True)
    unit = models.ForeignKey(StockUnit, null=True, on_delete=models.DO_NOTHING)
    packaging = models.CharField(max_length=HUNDRED, null=True, blank=True)
    has_variation = models.BooleanField(default=False)

    objects = ProductManager()

    def __str__(self):
        return self.product_name

    def get_category_list(self):
        k = self.category  # for now ignore this instance method

        breadcrumb = ["dummy"]
        while k is not None:
            breadcrumb.append(k.slug)
            k = k.parent
        for i in range(len(breadcrumb) - 1):
            breadcrumb[i] = "/".join(breadcrumb[-1 : i - 1 : -1])
        return breadcrumb[-1:0:-1]

    def get_photo_url(self):
        return f"https://cdn.phurti.in/phurti-cloudfront/{self.photo}"

    def save(self, *args, **kwargs):
        if not self.sku:
            last_sku = Product.objects.all().order_by("id").last()
            if not last_sku:
                self.sku = "SKU00000001"
            else:
                self.sku = last_sku.sku
                product_sku_int = int(self.sku.split("SKU")[-1])
                new_product_sku_int = product_sku_int + 1
                new_sku = "SKU00000000"[
                    : len("SKU00000000") - len(str(new_product_sku_int))
                ] + str(new_product_sku_int)
                self.sku = new_sku

        super(Product, self).save(*args, **kwargs)

    def current_price_variation(self, inventory_id):
        if inventory_id:
            sellable_inventory = SellableInventory.objects.filter(
                product=self, inventory_id=inventory_id
            ).first()
            if sellable_inventory:
                price_variations = (
                    sellable_inventory.sellable_product_price_variation.all()
                )
                for price_variation in price_variations:
                    valid_from = price_variation.valid_from
                    valid_to = price_variation.valid_to
                    if valid_from:
                        if valid_to:
                            if valid_from <= now() < valid_to:
                                return price_variation
                        else:
                            if valid_from <= now():
                                return price_variation
        return None


class SellableInventory(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    inventory = models.ForeignKey(
        Inventory, related_name="sellable_inventories", on_delete=models.DO_NOTHING
    )
    product = models.ForeignKey(
        Product, related_name="sellable_products", on_delete=models.DO_NOTHING
    )
    is_active = models.BooleanField(default=True)
    quantity_remaining = models.FloatField(default=ZERO)
    address = models.CharField(max_length=SIX, null=True, blank=True)
    expiry = models.DateField(null=True)
    batch_number = models.CharField(max_length=HUNDRED, null=True)

    def add_price(self, price=None, market_price=None):
        price_variations = ProductPriceVariation.objects.filter(sellable_inventory=self)
        last_variation = price_variations.last()
        if last_variation:
            if not last_variation.price == price:
                last_variation.valid_to = datetime.now()
                last_variation.save()
                ProductPriceVariation.objects.create(
                    sellable_inventory=self, price=price, valid_from=datetime.now()
                )
        else:
            ProductPriceVariation.objects.create(
                sellable_inventory=self, price=price, valid_from=datetime.now()
            )


class ProductPriceVariation(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    sellable_inventory = models.ForeignKey(
        SellableInventory,
        related_name="sellable_product_price_variation",
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    price = models.DecimalField(
        verbose_name="Our Price", max_digits=TWENTY, decimal_places=FOUR
    )
    market_price = models.DecimalField(
        verbose_name="Market Price",
        max_digits=TWENTY,
        decimal_places=FOUR,
        null=True,
        blank=True,
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)


class DeliveryType(TimeStamped):
    type = models.CharField(max_length=HUNDRED, choices=DELIVERY_TYPES)

    def __str__(self):
        return self.type


class CartItem(TimeStamped):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=TWENTY, decimal_places=FOUR, default=1.0)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )  # TO be deleted later
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    final_price = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, blank=True, null=True, default=0
    )  # price after adding discount
    discount_code = models.ForeignKey(
        Discount, on_delete=models.CASCADE, null=True, blank=True
    )  # dispunt code detail

    def __str__(self):
        return f"{str(self.quantity)} of {self.product.product_name}"

    def get_total_cartitem_price(self):
        price_variation = self.product.current_price_variation(
            self.customer.inventory_id
        )
        if price_variation:
            return Decimal(price_variation.price) * Decimal(self.quantity)
        return Decimal(price_variation.price) * Decimal(self.quantity)

    def save(self, *args, **kwargs):
        if not self.discount_code and not self.final_price:
            self.final_price = self.get_total_cartitem_price()

        if not self.discount_code and self.final_price:
            self.final_price = self.get_total_cartitem_price()

        super(CartItem, self).save(*args, **kwargs)


class Cart(TimeStamped):
    cartitem = models.ManyToManyField(CartItem, verbose_name="cart")
    status = models.CharField(
        max_length=TWO_HUNDRED, choices=CART_STATUS_TYPES, verbose_name="cartStatus"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )  # To be Deleted later
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    total_price = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, default=0.0
    )
    tenant = models.ForeignKey(
        account.models.Tenant, on_delete=models.CASCADE, default=1
    )

    def __str__(self):
        if self.customer:
            return f"Cart ({self.id})"
        else:
            return f"{self.user.phone} ({self.id})"

    def get_total_price(self, cartitems=None):
        total_price = self.total_price
        if cartitems:
            total_price = 0
            for item in cartitems:
                total_price += item.get_total_cartitem_price()
        return total_price

    def get_total_unit_price(self, cart_items=None):
        total = Decimal(0)
        cartitems = self.cartitem.all()
        if cart_items:
            cartitems = cart_items
        for item in cartitems:
            try:
                price_variation = item.product.current_price_variation(
                    self.customer.inventory_id
                )
                if price_variation:
                    price_variation = price_variation.price
                else:
                    price_variation = item.product.price
            except Exception as err:
                logger.error(err)
                price_variation = item.product.price
            value = Decimal(price_variation) * Decimal(item.quantity)
            total += value
        return total

    def get_total_item(self):
        total = 0
        for order_item in self.cartitem.all():
            total += order_item.quantity
        return total

    def get_order_list(self):
        final = ""
        for p in self.cartitem.all():
            final += f"{str(p.product.product_name)}, (Description={str(p.product.description)}),(Quantity={str(p.quantity)} ),\n"
        return final


class OrderManager(models.Manager):
    def initialize(self, user):
        prev_active_orders = Order.objects.filter(
            customer=user,
            status__in=[Status.INITIALISED.value, Status.INVOICE_GENERATED.value],
        )
        if prev_active_orders:
            # order_obj = Order.objects.create(customer=user, status=Status.INITIALISED.value)
            # return order_obj
            raise ValueError("Initialization not allowed")
        else:
            order_obj = Order.objects.create(
                customer=user, status=Status.INITIALISED.value, inventory=user.inventory
            )
            try:
                users = Profile.objects.filter(
                    Q(inventory=user.inventory, role="SK") | Q(role="ADMIN")
                )
                device_ids = []
                for user in users:
                    device_ids.append(user.device_id)
                message_title = "Order Initiated"
                message_body = "A new Order is Initiated"
                extra_notification_kwargs = {
                    "sound": "notification.wav",
                    "android_channel_id": "hello",
                }
                result = self.push_service.notify_multiple_devices(
                    registration_ids=device_ids,
                    message_title=message_title,
                    message_body=message_body,
                    extra_notification_kwargs=extra_notification_kwargs,
                )
            except Exception as err:
                logger.error(str(err))
            return order_obj


class Order(TimeStamped):
    ORDER_SOURCE = (("WEBSITE", ("WEBSITE")), ("BILLING", ("BILLING")))
    tenant = models.ForeignKey(
        account.models.Tenant, on_delete=models.CASCADE, default=1
    )
    fulfilment_type = models.CharField(
        max_length=HUNDRED,
        choices=FULFILMENT_TYPES,
        default=FulfilmentType.DELIVERY.value,
    )
    delivery_type = models.CharField(
        max_length=HUNDRED,
        choices=DELIVERY_TYPES,
        default=EXPRESS,
        null=True,
        blank=True,
    )
    customer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="orders"
    )
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, verbose_name="Cart", blank=True, null=True
    )
    payment_status = models.CharField(
        max_length=HUNDRED, choices=PAYMENT_STATUS_TYPES, default="PENDING"
    )
    fulfilment_address = models.CharField(
        max_length=ONE_THOUSAND,
        default=None,
        verbose_name="Fulfilment Address",
        null=True,
        blank=True,
    )
    delivery_address = models.CharField(
        max_length=ONE_THOUSAND,
        default=" ",
        verbose_name="Address",
        null=True,
        blank=True,
    )
    total_price = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, null=True, blank=True, default=0.0
    )
    packaging_charge = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, blank=True, null=True, default=0.00
    )
    delivery_charge = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, default=10.00
    )
    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, null=True, blank=True
    )
    prescription_url = models.URLField(blank=True, null=True)
    source = models.CharField(
        max_length=FIFTY, choices=ORDER_SOURCE, null=True, blank=True
    )
    state = JSONField(default=DEFAULT_ORDER_STATE)
    status = models.CharField(
        max_length=FIFTY, choices=Status.choices()
    )  # CREATING - USer confirm ->  Active (Tracking IN Transit ,  ) -> DELIVERED -> Order Cancel (Creation phase no data to show to user) -> past order list mein cancelled orders
    objects = OrderManager()

    def __str__(self):
        if self.customer:
            return f"{self.customer.phone_number}:{self.customer.name}'s Order! on {localtime(self.created_on).strftime('%d-%m-%Y at %H:%M')}"

    from pyfcm import FCMNotification
    from django.conf import settings

    push_service = FCMNotification(api_key=settings.FCM_API_KEY)

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)

    def get_next_actions(self, state_action):
        return ORDER_STATE_WORKFLOW.get(state_action, {})

    def append_states(self, states):
        state_list = self.state["state_list"]
        for state in states:
            state_list.append(state)
        self.state["state_list"] = state_list
        self.save()

        # Order.objects.raw(f"UPDATE shop_order SET state = jsonb_set(state, '{last_key+1}', '{state_value}', TRUE) WHERE id = {self.id}")


@receiver(pre_delete, sender=Order, dispatch_uid="Update Sallable Inventory Product")
def update_sellableinventory_product(sender, instance, **kwargs):
    if instance.payment_status not in [CHECKOUT, FAILED]:
        ordered_item = OrderItem.objects.filter(order_id__id=instance.id)
        if ordered_item:
            for item in ordered_item:
                recaptured_stock = SellableInventory.objects.filter(
                    inventory=item.order_id.inventory
                ).filter(product=item.product_id)
                if recaptured_stock:
                    stock = recaptured_stock.first()
                    stock.quantity_remaining += float(item.quantity)
                    stock.save()


class WastedProduct(TimeStamped):
    added_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.DecimalField(max_digits=TWENTY, decimal_places=FOUR, default=1.0)
    quantity_units = models.ForeignKey(StockUnit, on_delete=models.CASCADE, null=True)
    reason = models.TextField(default="None")
    image = models.ImageField(
        upload_to="wastedproduct", verbose_name="Wasted Product", null=True
    )

    def __str__(self):
        return self.product.product_name


class OrderItem(TimeStamped):
    title = models.CharField(max_length=HUNDRED, blank=True, null=True)
    description = models.CharField(
        "Order item description", blank=True, null=True, max_length=HUNDRED
    )
    expiry = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=HUNDRED, null=True, blank=True)
    order_id = models.ForeignKey(Order, null=True, blank=True, on_delete=models.CASCADE)
    product_id = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE
    )
    quantity = models.DecimalField(
        null=True,
        blank=True,
        max_digits=TWENTY,
        decimal_places=FOUR,
        default=Decimal("1"),
    )
    price = models.DecimalField(
        null=True,
        blank=True,
        max_digits=TWENTY,
        decimal_places=FOUR,
        default=Decimal("0"),
    )
    discount_code = models.ForeignKey(
        Discount, on_delete=models.CASCADE, null=True, blank=True
    )  # dispunt code detail
    final_price = models.DecimalField(
        null=True,
        blank=True,
        max_digits=TWENTY,
        decimal_places=FOUR,
        default=Decimal("0"),
    )

    def __str__(self):
        return f"{self.title}"


@receiver(post_save, sender=Order, dispatch_uid="update_order_item")
def update_order_item(sender, instance, **kwargs):
    created = False
    if kwargs["created"]:
        created = True
    if created:
        if instance.cart:
            carts = Cart.objects.filter(pk=instance.cart.id)
        else:
            carts = None
        if carts:
            pro = carts.first().cartitem.all()
            user = carts.first().customer
            for product in pro:
                try:
                    price_from_inv = product.product.current_price_variation(
                        user.inventory_id
                    )
                except Exception as err:
                    logger.error(err)
                    price_from_inv = product.product

                temp_price = product.quantity * product.product.price
                if price_from_inv:
                    temp_price = product.quantity * price_from_inv.price

                order_item = OrderItem.objects.create(
                    title=product.product.product_name,
                    description=product.product.description,
                    product_id=product.product,
                    quantity=product.quantity,
                    price=temp_price,
                    order_id=instance,
                    final_price=product.final_price,
                    discount_code=product.discount_code,
                )
                order_item.save()
                if order_item.discount_code:
                    discount_code = order_item.discount_code
                    one_time_use = discount_code.discount_attributes.filter(
                        one_time_per_user=True
                    ).first()
                    if one_time_use:
                        discount_code.is_applied = True
                        discount_code.save()


class PaymentDetails(models.Model):
    source = models.CharField(
        "Payment Source", max_length=FIFTY, choices=PAYMENT_SOURCES, default=WEBSITE
    )
    gateway_type = models.CharField(
        "Payment Gateway Type", null=True, blank=True, max_length=FIFTY
    )
    mode = models.CharField("Mode of payment", max_length=FIFTY, choices=PAYMENT_MODES)
    additional_details = models.TextField(
        "Extra Payment Details", null=True, blank=True
    )

    class Meta:
        abstract = True


class Payment(TimeStamped, PaymentDetails):
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, default=1)
    amount = models.DecimalField(
        "Total Amount",
        null=True,
        max_digits=TWENTY,
        decimal_places=FOUR,
        default=Decimal("0"),
    )  # item_total+discount_total
    txn_id = models.CharField(
        "Transaction ID", db_index=True, null=True, blank=True, max_length=FIFTY
    )
    status = models.CharField(
        "Status", null=True, blank=True, max_length=FIFTY, choices=PAYMENT_STATUS_TYPES
    )
    payment_date = models.DateTimeField(null=True)
    product_info = models.TextField("Product Info", null=True, blank=True)
    payment_id = models.CharField(
        "Payment ID", max_length=FIFTY, null=True, blank=True, db_index=True
    )
    refund_id = models.CharField(
        "Refund ID", max_length=FIFTY, null=True, blank=True, db_index=True
    )
    invoice_id = models.CharField(
        "Invoice ID", max_length=FIFTY, null=True, blank=True, db_index=True
    )
    order = models.ForeignKey(
        Order,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="payment_order",
    )

    def __str__(self):
        return f"{self.id}:{self.source},{self.mode},{self.additional_details}"


class Subscriptions(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, default=1)
    customer = models.ForeignKey(
        Customer,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )  # to be deleted later
    new_customer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True
    )
    products = models.ManyToManyField(Product)
    from_date = models.DateField()
    to_date = models.DateField()
    is_active = models.BooleanField(default=True)
    time_slot = models.TimeField()
    payment_id = models.ForeignKey(
        Payment,
        null=True,
        blank=True,
        related_name="payments",
        on_delete=models.CASCADE,
    )
    quantity = models.DecimalField(
        default=1.0, max_digits=TWENTY, decimal_places=TWO, blank=True, null=True
    )
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.new_customer:
            return f"{self.new_customer.name}: {self.from_date} -> {self.to_date}"
        else:
            return f"{self.customer.name}: {self.from_date} -> {self.to_date}"


class Invoice(TimeStamped):
    invoice_id = models.CharField(max_length=FIFTY, null=True, blank=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    invoice_url = models.URLField(blank=True, null=True)
    final_price = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, blank=True, null=True
    )

    def __str__(self):
        return f"{self.invoice_id}: {self.order_id}"

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            last_invoice = Invoice.objects.all().order_by("id").last()
            if not last_invoice:
                self.invoice_id = "INV00000001"
            else:
                self.invoice_id = last_invoice.invoice_id
                invoice_int = int(self.invoice_id.split("INV")[-1])
                new_invoice_int = invoice_int + 1
                new_invoice_id = "INV00000000"[
                    : len("INV00000000") - len(str(new_invoice_int))
                ] + str(new_invoice_int)
                self.invoice_id = new_invoice_id

        super(Invoice, self).save(*args, **kwargs)


class InvoiceItem(TimeStamped):
    title = models.CharField(max_length=HUNDRED, blank=True, null=True)
    description = models.CharField(
        "Invoice item description", blank=True, null=True, max_length=HUNDRED
    )
    quantity = models.DecimalField(
        max_digits=TWENTY, decimal_places=FOUR, blank=True, null=True
    )
    price = models.DecimalField(
        max_digits=TWENTY,
        decimal_places=FOUR,
        verbose_name="Invoice: Item Price",
        blank=True,
        null=True,
    )
    invoice_id = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="Invoice"
    )
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product Name",
        null=True,
        blank=True,
    )
    unit_id = models.ForeignKey(
        StockUnit, on_delete=models.CASCADE, verbose_name="Unit", null=True, blank=True
    )
    objects = InvoiceItemManager()

    def __str__(self):
        return f"{self.title} | {self.description} | {self.price}"


@receiver(post_save, sender=Order, dispatch_uid="Update invoice")
def update_invoice(sender, instance, **kwargs):
    check = Invoice.objects.filter(order_id=instance.id)
    if check:
        q = check.first().final_price
        check.update(final_price=instance.total_price)

    else:
        invoice_url_temp = "https://phurti.in/invoice/"
        invoice = Invoice.objects.create(
            order_id=instance,
            final_price=instance.total_price,
            invoice_url=invoice_url_temp + str(instance.id),
        )
        invoice.save()


@receiver(post_save, sender=Invoice, dispatch_uid="update invoice item")
def update_invoice_item(sender, instance, **kwargs):
    created = False
    if kwargs["created"]:
        created = True
    if created:
        if instance.order_id.cart:
            carts = Cart.objects.filter(pk=instance.order_id.cart.id)
        else:
            carts = None
        if carts:
            pro = carts.first().cartitem.all()
            for h in pro:
                invoice_item = InvoiceItem.objects.create(
                    product_id=h.product,
                    title=h.product.product_name,
                    description=h.product.description,
                    quantity=h.quantity,
                    price=h.product.price,
                    invoice_id=instance,
                )
                invoice_item.save()


# @receiver(post_save, sender=Invoice, dispatch_uid="Update Order")
# def update_invoice_from_order(sender, instance, **kwargs):
#     invoiceitem = InvoiceItem.objects.filter(invoice_id=instance.id)
#     final = ''
#     for p in invoiceitem:
#         final += f"{str(p.title)}, (Description={str(p.description)}),(Quantity={str(p.quantity)} ),\n"
#     final_price = instance.final_price
#     order = Order.objects.filter(pk=instance.order_id.id).update(total_price=final_price, orderlist=final)


class DailyInventoryTracker(TimeStamped):
    inventory_id = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, verbose_name="Product"
    )
    quantity_remaining = models.DecimalField(
        default=0.0,
        verbose_name="Quantity Remaining",
        max_digits=TWENTY,
        decimal_places=FOUR,
    )
    quantity_unit = models.ForeignKey(StockUnit, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.inventory_id} || {self.product_id} || {self.quantity_remaining} || {self.quantity_unit}"


# Order OTP scheduler
class OrderScheduler(TimeStamped):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    schedule_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{str(self.schedule_time)}--->{self.order_id}"


@receiver(post_save, sender=OrderScheduler)
def creating_cache_scheduler(sender, instance, **kwargs):
    dump_data = {
        "schedule_time": str(instance.schedule_time),
        "OTP_sent": False,
        "OrderId": str(instance.order_id.id),
    }
    date = str(instance.schedule_time).split(" ")[0]
    create_cache(dump_data, date)


# Favourite Products
class FavouriteProduct(TimeStamped):
    product_id = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{str(self.product_id)}--->{self.user_id}"


class Offers(TimeStamped):
    desktop_view_image = models.ImageField(
        upload_to="offers", verbose_name="Desktop View Image"
    )
    tablet_view_image = models.ImageField(
        upload_to="offers", verbose_name="Tablet View Image"
    )
    mobile_view_image = models.ImageField(
        upload_to="offers", verbose_name="Mobile View Image"
    )
    action_link = models.CharField(max_length=TWO_HUNDRED)
    priority = models.IntegerField(default=0)
    title = models.CharField(max_length=TWO_HUNDRED, null=True, blank=True)
    tenant = models.ForeignKey(
        account.models.Tenant, on_delete=models.CASCADE, default=1
    )

    def __str__(self):
        return str(self.title)


class VariationTypes(TimeStamped):
    name = models.CharField(max_length=HUNDRED)
    image = models.ImageField(
        upload_to="variation_types",
        verbose_name="Variation Image",
        null=True,
        blank=True,
    )
    description = models.TextField()
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "VariationTypes"


class VariationOptions(TimeStamped):
    variation_type = models.ForeignKey(VariationTypes, on_delete=models.CASCADE)
    name = models.CharField(max_length=HUNDRED)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "VariationOptions"


class ProductVariation(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_active = models.BooleanField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_variation = models.ForeignKey(ProductPriceVariation, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.product.product_name

    class Meta:
        verbose_name_plural = "ProductVariation"


class VariationCombos(TimeStamped):
    variation_options = models.ForeignKey(VariationOptions, on_delete=models.CASCADE)
    product_variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    tenant=models.ForeignKey(Tenant,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "VariationCombos"


class Toppings(TimeStamped):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    is_active = models.BooleanField(default=False)
    price = models.ForeignKey(ProductPriceVariation, models.CASCADE)
    name = models.CharField(max_length=HUNDRED)
    image = models.ImageField(
        upload_to="Toppins", verbose_name="Toppings Images", null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "Toppings"
