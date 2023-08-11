from django.conf import settings
from django.db import transaction
import re
import logging
import datetime
from .data.sql_utils import *

logger = logging.getLogger("phurti")


def get_value_from_dict_or_settings(settings_dict, data_dict, key):
    value = data_dict.get(key) or settings_dict.get(key)
    return value


def create_promotional_discount(order, discount_data):
    from shop.models import Discount, DiscountAttributes

    try:
        with transaction.atomic():
            customer = order.customer
            customer_name = "".join(customer.name.split(" ")) or "PHUR"
            if len(customer_name) < 5:
                discount_code = customer_name + str(order.id)
            else:
                discount_code = customer_name[:4] + str(order.id)
            discount_data_from_settings = settings.DISCOUNT_SETTINGS
            discount_obj = Discount.objects.create(
                discount_code_type=get_value_from_dict_or_settings(
                    discount_data_from_settings, discount_data, "discount_code_type"
                ),
                value=get_value_from_dict_or_settings(
                    discount_data_from_settings, discount_data, "value"
                ),
                maximum_discount=get_value_from_dict_or_settings(
                    discount_data_from_settings, discount_data, "maximum_discount"
                ),
                code=discount_code,
                code_description=f"Promotional Discount Code For {customer_name}",
                is_active=True,
                minimum_order_value=get_value_from_dict_or_settings(
                    discount_data_from_settings, discount_data, "minimum_order_value"
                ),
                apply_type=get_value_from_dict_or_settings(
                    discount_data_from_settings, discount_data, "apply_type"
                ),
            )
            category = get_value_from_dict_or_settings(
                discount_data_from_settings, discount_data, "discount_category"
            )
            discount_attribute_obj = DiscountAttributes.objects.create(
                discount=discount_obj,
                applied_on="customer",
                one_time_per_user=True,
                attribute_type="promotional",
            )
            discount_attribute_obj.customer.add(customer)

            # adding category if present for discount
            for category_id in category:
                discount_attribute_obj.category.add(category_id)

            return discount_obj
    except Exception as err:
        return Discount.objects.none()


def get_discounted_amount_cart(discount_obj, cart, data={}):
    if data.get("applied_on") and data.get("filtered_data"):
        cart_total_price = cart.get_total_unit_price(data.get("filtered_data"))
    else:
        cart_total_price = cart.get_total_unit_price()
    discount_code_type = discount_obj.discount_code_type
    discount_amount = 0
    if discount_code_type == "A":
        discount_amount = discount_obj.value
    elif discount_code_type == "P":
        discount_amount = (cart_total_price * discount_obj.value) / 100
    if discount_obj.maximum_discount < discount_amount:
        discount_amount = discount_obj.maximum_discount
    return discount_amount


def remove_discount(discount, cart):
    if cart.cartitem:
        for cartitem in cart.cartitem.all():
            temp_final_price = cartitem.get_total_cartitem_price()
            cartitem.final_price = temp_final_price
            cartitem.discount_code = None
            cartitem.save()
    discount.is_applied = False
    discount.save()
    cart.total_price = cart.get_total_unit_price()
    cart.save(update_fields=["total_price"])


def calculate_and_apply_discount(discount, cart):
    from shop.constants import INVENTORY, CATEGORY, PRODUCTS, CUSTOMER, OTHERS, ITEMS

    return_dict = {"status": False, "message": "Something Went Wrong"}
    can_apply_discount = False
    apply_type = discount.apply_type
    customer = cart.customer
    applied_on = list(discount.discount_attributes.values_list("applied_on", flat=True))
    inventory = list(discount.discount_attributes.values_list("inventory", flat=True))
    custom_data = {}
    if cart.get_total_price() < discount.minimum_order_value:
        return_dict[
            "message"
        ] = "Discount coupon minimum value should be {discount.minimum_order_value}"
        return_dict["custom_data"] = custom_data
        remove_discount(discount, cart)
        return return_dict

    if INVENTORY in applied_on and (customer.inventory.pk not in inventory):
        return_dict["message"] = "Discount coupon is not valid for your area."
        remove_discount(discount, cart)
        return return_dict
    elif CATEGORY in applied_on:
        category = discount.discount_attributes.values_list("category", flat=True)
        count = 0
        for category_id in list(category):
            filtered_items = cart.cartitem.filter(
                product__category_products__id=category_id
            )
            if list(filtered_items):
                count += 1
        if count != len(list(category)) and not filtered_items.exists():
            return_dict["message"] = "Discount coupon is not valid for selected items."
            remove_discount(discount, cart)
            return return_dict
        custom_data["applied_on"] = CATEGORY
        custom_data["filtered_data"] = filtered_items
        can_apply_discount = True
    elif PRODUCTS in applied_on:
        product = discount.discount_attributes.values_list("product", flat=True)
        filtered_items = cart.cartitem.filter(product__id__in=product)
        if not filtered_items.exists():
            return_dict[
                "message"
            ] = "Discount coupon is not valid for selected products."
            remove_discount(discount, cart)
            return return_dict
        custom_data["applied_on"] = PRODUCTS
        custom_data["filtered_data"] = filtered_items
        can_apply_discount = True
    elif CUSTOMER in applied_on:
        discount_customers = discount.discount_attributes.filter(customer=customer)
        if not discount_customers.exists():
            return_dict["message"] = "Discount coupon is not valid"
            remove_discount(discount, cart)
            return return_dict
        can_apply_discount = True
    elif OTHERS in applied_on:
        can_apply_discount = True
    if apply_type == ITEMS:
        custom_data["apply_type"] = ITEMS
        can_apply_discount = True
    if not can_apply_discount:
        return_dict["message"] = "Discount coupon is not valid."
        remove_discount(discount, cart)
        return return_dict
    return_dict["message"] = "SUCCESS"
    return_dict["status"] = True
    return_dict["custom_data"] = custom_data
    return return_dict


def check_phoneNumber(s):
    Pattern = re.compile("^(\+91[\-\s]?)?[0]?(91)?[789]\d{9}$")
    print(Pattern.match(s))
    return Pattern.match(s)


def update_discount_code(order):
    from shop.models import OrderItem
    from shop.constants import SUCCESS, CASH

    try:
        if order.payment_status == SUCCESS or order.mode_of_payment == CASH:
            order_item_list = OrderItem.objects.filter(order_id=order)
            if order_item_list:
                for order_item in order_item_list:
                    if order_item.discount_code:
                        discount_code = order_item.discount_code
                        one_time_use = discount_code.discount_attributes.filter(
                            one_time_per_user=True
                        ).first()
                        if one_time_use:
                            discount_code.is_applied = True
                            discount_code.save()
    except Exception as e:
        logger.error(e)


def fetch_leaf_category(category):
    leaf_categories = set()
    indegree = {}
    outdegree = {}

    for category_obj in category:
        indegree[category_obj] = 0
        outdegree[category_obj] = 0

    for category_obj in category:
        print(category_obj, category_obj.parent)
        if category_obj.parent:
            indegree[category_obj] += 1
            outdegree[category_obj.parent] += 1

    for cate, out_edge in outdegree.items():
        if out_edge == 0:
            leaf_categories.add(cate)

    return leaf_categories


# Delivery charge utils

DELIVERY_CHARGES = settings.DELIVERY_CHARGES


def _time(time):
    return datetime.datetime.strptime(time, "%H:%M:%S")


def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:  # Over midnight
        return nowTime >= startTime or nowTime <= endTime


def get_delivery_charge():
    current = datetime.datetime.strptime(
        datetime.datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S"
    )
    try:
        for charges in DELIVERY_CHARGES["variables"]:
            if isNowInTimePeriod(
                _time(charges["start_time"]), _time(charges["end_time"]), current
            ):
                return charges["amount"]
        return DELIVERY_CHARGES["default"]
    except:
        return DELIVERY_CHARGES["default"]


def get_default_delivery_charge():
    return DELIVERY_CHARGES["default"]


def get_deliverychange_time():
    current = datetime.datetime.strptime(
        datetime.datetime.now().time().strftime("%H:%M:%S"), "%H:%M:%S"
    )
    default_current = current.time().strftime("%I %p")
    try:
        for charges in DELIVERY_CHARGES["variables"]:
            if isNowInTimePeriod(
                _time(charges["start_time"]), _time(charges["end_time"]), current
            ):
                return datetime.datetime.strptime(
                    charges["start_time"], "%H:%M:%S"
                ).strftime("%I %p")
        return default_current
    except:
        return default_current


def get_inventory_status():
    DELIVERY_ALERTS = settings.DELIVERY_ALERTS
    return DELIVERY_ALERTS


def verify_stocks(cart, inventory):
    from shop.models import SellableInventory

    products = cart.cartitem.all()
    out_of_stock_products_id = []
    try:
        for product in products:
            temp_sellable_inventory = SellableInventory.objects.filter(
                inventory=inventory, product=product.product
            ).first()
            if temp_sellable_inventory:
                temp_quantity_remaining = float(
                    temp_sellable_inventory.quantity_remaining
                )
                if temp_quantity_remaining < float(product.quantity):
                    out_of_stock_products_id.append(product.product.id)

    except Exception as e:
        logger.error(e)

    return out_of_stock_products_id


def arrange_stocking_data(inventory_id):
    final_data = []
    results = []
    data = Product_details()
    product_remaining = {}
    category = {}
    cache = set()
    # processing data
    for detail in data["data"]:
        product_data = {}
        for index in range(len(detail)):
            product_data[data["desc"][index]] = detail[index]

        final_data.append(product_data)

    # processing inventory product remaning and price variations
    pricevariation_id = 0
    for product in final_data:
        data = {
            "inventory_id": product["inventory_id"],
            "product_remaining": product["quantity_remaining"],
            "market_price": product["market_price"],
            "price": product["price"],
            "address": product["address"],
        }
        if product["inventory_id"] and int(inventory_id) == int(
            product["inventory_id"]
        ):
            if product["id"] in product_remaining:
                if product["pricevariation_id"] and pricevariation_id < int(
                    product["pricevariation_id"]
                ):
                    product_remaining[product["id"]].pop()
                if data not in product_remaining[product["id"]]:
                    product_remaining[product["id"]].append(data)
            else:
                product_remaining[product["id"]] = [data]

    # Processing category
    for product in final_data:
        data = product["name"]
        if product["id"] in category:
            if data not in category[product["id"]]:
                category[product["id"]].append(data)
        else:
            category[product["id"]] = [data]

    # final processing
    for product in final_data:
        try:
            product["title"] = product["product_name"]
            product["category"] = category[product["id"]]
            product["price_variation"] = product_remaining[product["id"]]
            product["remaining_products"] = product_remaining[product["id"]]
            product[
                "photo"
            ] = f"https://cdn.phurti.in/phurti-cloudfront/{product['photo']}"
        except Exception as err:
            logger.error(err)
            product["category"] = []
            product["remaining_products"] = []
            product["price_variation"] = []
        result = product["id"]
        if result not in cache:
            results.append(product)
            cache.add(result)

    return results


def arrange_data(inventory_id):
    final_data = []
    results = []
    data = Product_details()
    stockunits = StockUnits()
    product_remaining = {}
    category = {}
    cache = set()
    # processing data
    for detail in data["data"]:
        product_data = {}
        for index in range(len(detail)):
            product_data[data["desc"][index]] = detail[index]

        final_data.append(product_data)

    # processing inventory product remaning and price variations
    pricevariation_id = 0
    for product in final_data:
        data = {
            "inventory_id": product["inventory_id"],
            "product_remaining": product["quantity_remaining"],
            "market_price": product["market_price"],
            "price": product["price"],
            "address": product["address"],
        }
        if product["inventory_id"] and int(inventory_id) == int(
            product["inventory_id"]
        ):
            if product["id"] in product_remaining:
                if product["pricevariation_id"] and pricevariation_id < int(
                    product["pricevariation_id"]
                ):
                    product_remaining[product["id"]].pop()
                if data not in product_remaining[product["id"]]:
                    product_remaining[product["id"]].append(data)
            else:
                product_remaining[product["id"]] = [data]

    # Processing category
    for product in final_data:
        data = product["name"]
        if product["id"] in category:
            if data not in category[product["id"]]:
                category[product["id"]].append(data)
        else:
            category[product["id"]] = [data]

    units = {}
    for unit in stockunits["data"]:
        units[unit[0]] = unit[3]

    # final processing
    for product in final_data:
        try:
            product["title"] = product["product_name"]
            product["category"] = category[product["id"]]
            product["price_variation"] = product_remaining[product["id"]]
            product["remaining_products"] = product_remaining[product["id"]]
            product[
                "photo"
            ] = f"https://cdn.phurti.in/phurti-cloudfront/{product['photo']}"
            product["unit"] = units[product["unit_id"]]
        except Exception as err:
            logger.error(err)
            product["category"] = []
            product["remaining_products"] = []
            product["price_variation"] = []
        result = (product["id"], product["expiry"], product["batch_number"])
        if result not in cache:
            results.append(product)
            cache.add(result)

    return results
