from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import *
import os
from shop.enums import *
from shop.custom_s3_storage import MediaStorage
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
import http.client
import json, calendar
from rest_framework import generics, viewsets
from .paginations import *
from decimal import Decimal
from account.models import *
from django.db.models import F
from django.http.response import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes, renderer_classes
from django.utils.timezone import make_aware
from datetime import datetime, date
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from phurti.mixins import ToCamelCase, FromCamelCase

# from scripts.put_detail import
from account.models import Profile
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
import logging
from shop.utils import *
from phurti import settings
from .data.sql_utils import *
from .constants import *
from notifications.utils import parse_number
from notifications.views import send_order_communication
from pyfcm import FCMNotification
from shop.utils import check_phoneNumber
from django.db.models import Q
from .utils import fetch_leaf_category
from phurti.decorators.inventory_active import *
from phurti.commons.camelSnakeCaseTransformer.renderers import CamelCaseRenderer
from phurti.commons.camelSnakeCaseTransformer.parsers import SnakeCaseParser
from contactus.models import *
from shop.actions.utils import *
from phurti.models import *
from phurti.decorators.set_user import set_user

push_service = FCMNotification(api_key=settings.FCM_API_KEY)
from phurti.decorators.set_user import set_user


DISCOUNT_SETTINGS = settings.DISCOUNT_SETTINGS

logger = logging.getLogger("phurti")


def VoiceOTPsend(PHONE):
    TOKEN = settings.API_KEY_2FACTOR
    if TOKEN:
        if settings.OTP_SEND:
            conn = http.client.HTTPConnection("2factor.in")
            payload = ""
            headers = {"content-type": "application/x-www-form-urlencoded"}
            for j in PHONE:
                conn.request("GET", f"/API/V1/{TOKEN}/VOICE/{j}/1111", payload)
                res = conn.getresponse()
                data = res.read()
                response = {
                    "status": status.HTTP_200_OK,
                    "data": json.loads(data.decode("utf-8")),
                }


def OTPsend(PHONE):
    TOKEN = settings.API_KEY_2FACTOR
    if TOKEN:
        if settings.OTP_SEND:
            conn = http.client.HTTPConnection("2factor.in")
            payload = ""
            headers = {"content-type": "application/x-www-form-urlencoded"}
            for j in PHONE:
                conn.request(
                    "GET", f"/API/V1/{TOKEN}/SMS/{j}/Phuti/Send%20OTP", payload, headers
                )
                res = conn.getresponse()
                data = res.read()
                response = {
                    "status": status.HTTP_200_OK,
                    "data": json.loads(data.decode("utf-8")),
                }
            # prDecimal.from_float(float(response)


@api_view(["GET"])
def get_category(request, *args, **kwargs):
    tenant = Category.objects.filter(tenant=request.tenant_id).first()
    if tenant == None:
        return Response(
            {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
            status=status.HTTP_200_OK,
        )
    else:
        leaf = request.GET.get("leaf")
        category = Category.objects.filter(
            active=True, tenant=request.tenant_id
        ).order_by(F("priority").asc(nulls_last=True))
        if leaf:
            category = fetch_leaf_category(category)
        if category:
            data = CategorySerializer(category, many=True)
            return Response(
                {
                    "data": data.data,
                    "status": status.HTTP_200_OK,
                    "message": "Categories are fetched!",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                status=status.HTTP_200_OK,
            )


@api_view(["GET"])
def get_all_category(request):

    tenant = Category.objects.filter(tenant=request.tenant_id).first()
    if tenant == None:
        return Response(
            {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
            status=status.HTTP_200_OK,
        )
    else:
        category_ids = set()
        # Raw sql query to get category using left join
        if request.user.is_anonymous:
            inventory = Inventory.objects.filter(tenant=request.tenant_id)
            if not inventory:
                inventory=0
            else:
                inventory = inventory.first().id
        else:
            inventory = request.user.inventory.id

        sellable_category = UniqueCategorys(inventory_id=inventory)
        category = Category.objects.filter(
            active=True, pk__in=sellable_category, tenant_id=request.tenant_id
        )
        # for matching certain category in the requested inventory.
        for category_object in category:
            if category_object.parent:
                category_ids.add(category_object.parent.id)
            else:
                category_ids.add(category_object.id)
        final_category = (
            Category.objects.filter(pk__in=list(category_ids))
            .filter(~Q(name=EXTERNAL))
            .order_by(F("priority").asc(nulls_last=True))
        )
        if final_category:
            data = CategorySerializer(final_category, many=True)
            return Response(
                {
                    "data": data.data,
                    "status": status.HTTP_200_OK,
                    "message": "Categories are fetched!",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                status=status.HTTP_200_OK,
            )


# @api_view(["GET"])
# def get_product_list(request, *args, **kwargs):
#     category = kwargs.get('category')
#     if category=="all":
#         data = Product.objects.all().order_by('product_name')
#     elif category.lower()=="best sellers":
#         r = [24, 33, 13, 21]
#         # r = [1,2]
#         data = Product.objects.filter(pk__in=r).filter(is_active_product=True)
#     elif category.lower()=="gifts and chocolates":
#         data = Product.objects.filter(category__name=category).filter(is_active_product=True).order_by("-updated_on")
#     elif category.lower()=="beverages":
#         data = Product.objects.filter(category__name=category).filter(is_active_product=True).order_by("-updated_on")
#     elif category.lower()=="healthy drinks":
#         data = Product.objects.filter(category__name=category).filter(is_active_product=True).order_by("-updated_on")
#     else:
#         data = Product.objects.filter(category__name=category).filter(is_active_product=True)
#     serializer = ProductSerializer(data, many=True)
#     if data:
#         return Response({"data": serializer.data,"status": status.HTTP_200_OK,"message": "Products are fetched!"})
#     else:
#         return Response({"data": [], "status": status.HTTP_200_OK,"message": "Product list is empty!"}, status=status.HTTP_200_OK)


# get_product_list a/c to the inventory
@api_view(["GET"])
@set_user
def get_product_list(request, *args, **kwargs):
    category = kwargs.get("category")
    categoryid = kwargs.get("categoryid")
    category_products = Category.objects.filter(
        tenant=request.tenant_id, name=category, pk=categoryid
    ).first()
    if not request.user:
        inventory = Inventory.objects.filter(tenant=request.tenant_id)
        if not inventory:
            inventory=0
        else:
            inventory = inventory.first().id
    else:
        inventory = request.user.inventory.id
    if not category_products:
        return Response(
            {
                "data": [],
                "status": status.HTTP_200_OK,
                "message": "Product list is empty!",
            },
            status=status.HTTP_200_OK,
        )

    if not category_products.parent and not category_products.products.all():
        subcategory = Category.objects.filter(parent=category_products)
        product_pk = []
        for product in subcategory:
            product_pk.extend(product.products.all())
        product_list = SellableInventory.objects.filter(
            inventory_id=inventory, product__in=product_pk
        ).filter(product__is_active_product=True)

    else:
        product_list = SellableInventory.objects.filter(
            inventory_id=inventory,
            product__in=category_products.products.all(),
        ).filter(product__is_active_product=True)

    serializer = SellableInventorySerializer(
        product_list, many=True, context={"request": request}
    )
    if product_list:
        final_response = []
        for data in serializer.data:
            temp = dict(data["product"])
            temp["quantity_remaining"] = data["quantity_remaining"]

            final_response.append(temp)

        return Response(
            {
                "data": final_response,
                "status": status.HTTP_200_OK,
                "message": "Products are fetched!",
            }
        )
    else:
        return Response(
            {
                "data": [],
                "status": status.HTTP_200_OK,
                "message": "Product list is empty!",
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(
    request, *args, **kwargs
):  # Add to cart for only adding bulk items at a time
    # phone = kwargs.get("phone") #USER for ORDER
    # name = kwargs.get("name")
    # user = User.objects.filter(name=name, phone=phone)
    # if user:
    #     user = user.first()
    # else:
    #     user = User.objects.create(
    #         name=name,
    #         phone=phone
    #     )
    #     user.save()
    data = CartItemSerializer(data=request.data)
    cart = None
    tenant = get_object_or_404(Tenant, id=request.tenant_id)
    if data.is_valid():
        for j in data.data["items"]:
            f = {}
            for key, value in j.items():
                f[key] = value
            # prDecimal.from_float(float(f)
            product = get_object_or_404(Product, pk=f["product"])
            if float(f["quantity"]) > 0:
                cartitem = CartItem.objects.filter(
                    product=product, customer=request.user, is_active=True
                )
                if cartitem:
                    cartitem = cartitem.first()
                    discount_code = cartitem.discount_code
                    if discount_code and discount_code.is_applied:
                        discount_code.is_applied = False
                        discount_code.save()
                else:
                    print(request.user)

                    cartitem = CartItem.objects.create(
                        product=product, customer=request.user, is_active=True
                    )
                    cartitem.save()

            else:
                cartitem = CartItem.objects.filter(
                    product=product, customer=request.user, is_active=True
                )
                cartitem.delete()
            tenant = Tenant.objects.get(id=request.tenant_id)
            cart = Cart.objects.filter(
                customer=request.user, status="ACTIVE", tenant=tenant
            )
                   
            if cart.exists():
                cart = cart.first()
                if cart.cartitem.filter(product__pk=product.pk).exists():
                    if float(f["quantity"]) > 0:
                        cartitem.quantity = f["quantity"]
                        cartitem.save()
                else:
                    if float(f["quantity"]) > 0:
                        cartitem.quantity = f["quantity"]
                        cartitem.save()
                        cart.cartitem.add(cartitem)
            else:
                tenant = Tenant.objects.get(id=request.tenant_id)
                cart = Cart.objects.create(
                    customer=request.user, tenant=tenant
                )
                if cartitem:
                    cartitem.quantity = Decimal.from_float(float(f["quantity"]))
                    cartitem.save()
                    cart.cartitem.add(cartitem)
                cart.status = "ACTIVE"
                cart.save()
        if cart:
            cart.refresh_from_db()
            if cart.cartitem.count() > 0:
                cart_total_price = cart.get_total_price(cartitems=cart.cartitem.all())
                discount_cart_items = cart.cartitem.filter(discount_code__isnull=False)
                cart.total_price = cart_total_price
                if discount_cart_items.exists():
                    cart_item = discount_cart_items.first()
                    discount_obj = cart_item.discount_code
                    cart.cartitem.update(discount_code=discount_obj)
                    cart.refresh_from_db()
                    # if discount_obj.apply_type == CART:
                    #     cart.total_price = cart_total_price - get_discounted_amount_cart(discount_obj, cart)
                    # else:
                    calculated_data = calculate_and_apply_discount(discount_obj, cart)
                    if calculated_data.get("status", False):
                        custom_data = calculated_data.get("custom_data", {})
                        discount_obj.apply_discount(cart, custom_data)
                    # else:
                    #     message = calculated_data.get("message")
                    # return Response({"message": message,
                    #                     "status": status.HTTP_400_BAD_REQUEST},
                    #                 status=status.HTTP_400_BAD_REQUEST)
                    cart.total_price = cart.get_total_price()
                cart.save(update_fields=["total_price"])
            else:
                cart.total_price = 0
                cart.save(update_fields=["total_price"])
    else:
        return Response(
            {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"status": status.HTTP_201_CREATED, "message": "Item added to cart!"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart_one(
    request, *args, **kwargs
):  # Add to cart for only adding 1 item at a time
    data = CartItemOneSerializer(data=request.data)
    if data.is_valid():

        product = get_object_or_404(Product, pk=data.data["product"])
        if float(data.data["quantity"]) > 0:
            cartitem = CartItem.objects.filter(
                product=product, customer=request.user, is_active=True
            )
            if cartitem:
                cartitem = cartitem.first()
            else:
                cartitem = CartItem.objects.create(
                    product=product, customer=request.user, is_active=True
                )
                cartitem.save()

        else:
            cartitem = CartItem.objects.filter(
                product=product, customer=request.user, is_active=True
            )
            cartitem.delete()

        cart = Cart.objects.filter(customer=request.user, status="ACTIVE")
        if cart.exists():
            cart = cart[0]
            if cart.cartitem.filter(product__pk=product.pk).exists():
                if float(data.data["quantity"]) > 0:
                    cartitem.quantity = data.data["quantity"]
                    cartitem.save()

            else:
                if float(data.data["quantity"]) > 0:
                    cartitem.quantity = data.data["quantity"]
                    cartitem.save()
                    cart.cartitem.add(cartitem)

        else:

            cart = Cart.objects.create(customer=request.user)
            if cartitem:
                cartitem.quantity = Decimal.from_float(float(data.data["quantity"]))
                cartitem.save()
                cart.cartitem.add(cartitem)
            cart.status = "ACTIVE"
            cart.save()
    else:
        return Response(
            {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"status": status.HTTP_201_CREATED, "message": "Item added to cart!"},
        status=status.HTTP_201_CREATED,
    )


# def remove_from_cart(request, pk, **kwargs):
#     product = get_object_or_404(Product, pk=pk )
#     phone = kwargs.get("phone")
#     user = get_object_or_404(User, phone=phone)
#     cart = Cart.objects.filter(
#         user=user[0],
#         status="ACTIVE"
#     )
#     if cart.exists():
#         order = cart[0]
#         if order.items.filter(product__pk=product.pk).exists():
#             order_item = CartItem.objects.filter(
#                 product=product,
#                 user=user[0],
#             )[0]
#             order_item.delete()
#             # messages.info(request, "Item \""+order_item.item.item_name+"\" remove from your cart")
#             # return redirect("core:order-summary")
#         else:
#             pass
#             # messages.info(request, "This Item not in your cart")
#             # return redirect("core:product", pk=pk)
#     else:
#         pass
#         #add message doesnt have order
#         # messages.info(request, "You do not have an Order")
#         # return redirect("core:product", pk = pk)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@set_user
def get_cart(request, *args, **kwargs):
    data = Cart.objects.filter(
        tenant=request.tenant_id, customer=request.user, status="ACTIVE"
    )
    cartdetail = []
    if len(data) > 0:
        discount_code = ""
        for j in list(data[0].cartitem.all()):
            final_remaining_product = (
                SellableInventory.objects.filter(
                    inventory_id=request.user.inventory, product=j.product.pk
                )
                .filter(product__is_active_product=True)
                .first()
            )

            quantity_remaining = 0
            if final_remaining_product:
                quantity_remaining = final_remaining_product.quantity_remaining
            category = ""
            if j.product.category:
                category = j.product.category.name

            try:
                product_price = j.product.current_price_variation(
                    request.user.inventory_id
                )
                if product_price:
                    product_price = product_price.price
                else:
                    product_price = j.product.price
            except Exception as err:
                logger.error(str(err))
                product_price = j.product.price

            cart_data = {
                "product_name": j.product.product_name,
                "quantity": j.quantity,
                "original_price": product_price,
                "description": j.product.description,
                "id": j.product.pk,
                "photo": j.product.get_photo_url(),
                "category": category,
                "final_price": j.final_price,
                "quantity_remaining": quantity_remaining,
            }
            if j.discount_code:
                cart_data["discount_code"] = j.discount_code.code
                discount_code = j.discount_code.code
            else:
                cart_data["discount_code"] = None

            cartdetail.append(cart_data)
        final_price = data[0].get_total_price()
        final_item = data[0].get_total_item()
    serializer = CartSerializer(data, many=True)
    if data:
        return Response(
            {
                "discount_code": discount_code,
                "final_item": final_item,
                "final_price": final_price,
                "cartitem": cartdetail,
                "data": serializer.data,
                "status": status.HTTP_200_OK,
                "message": "Products are fetched!",
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "data": [],
                "status": status.HTTP_200_OK,
                "message": "Product list is empty!",
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def add_discount(request, *args, **kwargs):
    if request.method == "POST":
        try:
            custom_data = {}
            data = CartDiscountSerializer(data=request.data)
            is_valid_data = data.is_valid()
            if not is_valid_data:
                return Response(
                    {"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid Data"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                cart = Cart.objects.filter(
                    customer=request.user, status="ACTIVE"
                ).first()
                # if cart.cartitem:
                if not cart:
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Cart Not Found",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                for cartitem in cart.cartitem.all():
                    temp_final_price = cartitem.get_total_cartitem_price()
                    cartitem.final_price = temp_final_price
                    cartitem.discount_code = None
                    cartitem.save()

                cart.total_price = cart.get_total_price(cartitems=cart.cartitem.all())
                cart.save()
                try:
                    discount = Discount.objects.get(
                        code=data.data["discount_code"].upper(), is_active=True
                    )
                except Exception as err:
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Discount coupon not found",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if not discount.is_valid:
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Discount coupon is expired",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif discount.is_applied:
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "Discount coupon has already been applied",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif cart.get_total_price(cartitems=cart.cartitem.all()) < Decimal(
                    discount.minimum_order_value
                ):
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": f"To apply coupon you need to order minimum value of {discount.minimum_order_value}",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    # CHECK ATTRIBUTES LEVEL NOW.
                    can_apply_discount = False
                    apply_type = discount.apply_type
                    applied_on = list(
                        discount.discount_attributes.values_list(
                            "applied_on", flat=True
                        )
                    )
                    inventory = list(
                        discount.discount_attributes.values_list("inventory", flat=True)
                    )
                    if INVENTORY in applied_on and (
                        request.user.inventory.pk not in inventory
                    ):
                        return Response(
                            {
                                "status": status.HTTP_400_BAD_REQUEST,
                                "message": "Discount coupon is not valid for your area.",
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    elif CATEGORY in applied_on:
                        category = discount.discount_attributes.values_list(
                            "category", flat=True
                        )
                        discount_not_for = (
                            Category.objects.filter(~Q(products=None))
                            .exclude(pk__in=list(category))
                            .values_list("pk", flat=True)
                        )  # category which is not be included for discount
                        filtered_items = cart.cartitem.filter(
                            product__category_products__id__in=category
                        ).filter(
                            ~Q(
                                product__category_products__id__in=list(
                                    discount_not_for
                                )
                            )
                        )
                        if not filtered_items.exists():
                            return Response(
                                {
                                    "status": status.HTTP_400_BAD_REQUEST,
                                    "message": "Discount coupon is not valid for selected items.",
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        custom_data["applied_on"] = CATEGORY
                        custom_data["filtered_data"] = filtered_items
                        can_apply_discount = True
                    elif PRODUCTS in applied_on:
                        product = discount.discount_attributes.values_list(
                            "product", flat=True
                        )
                        filtered_items = cart.cartitem.filter(product__id__in=product)
                        if not filtered_items.exists():
                            return Response(
                                {
                                    "status": status.HTTP_400_BAD_REQUEST,
                                    "message": "Discount coupon is not valid for selected products.",
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        custom_data["applied_on"] = PRODUCTS
                        custom_data["filtered_data"] = filtered_items
                        can_apply_discount = True
                    elif CUSTOMER in applied_on:
                        discount_customers = discount.discount_attributes.filter(
                            customer=request.user
                        )
                        category = discount.discount_attributes.values_list(
                            "category", flat=True
                        )
                        discount_not_for = (
                            Category.objects.filter(~Q(products=None))
                            .exclude(pk__in=list(category))
                            .values_list("pk", flat=True)
                        )  # category which is not be included for discount
                        filtered_items = cart.cartitem.filter(
                            product__category_products__id__in=category
                        ).filter(
                            ~Q(
                                product__category_products__id__in=list(
                                    discount_not_for
                                )
                            )
                        )

                        if not filtered_items and not discount_customers.exists():
                            return Response(
                                {
                                    "status": status.HTTP_400_BAD_REQUEST,
                                    "message": "Discount coupon is not valid",
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        customer = request.user
                        if discount.discount_attributes.filter(
                            attribute_type="promotional"
                        ).exists():
                            customer_applied_discounts = (
                                customer.discountattributes_set.filter(
                                    discount__is_applied=True,
                                    applied_on=CUSTOMER,
                                    one_time_per_user=True,
                                    attribute_type="promotional",
                                )
                            )
                            if customer_applied_discounts.count() > int(
                                DISCOUNT_SETTINGS.get("maximum_count"), 0
                            ):
                                discount.is_active = False
                                discount.save()
                                return Response(
                                    {
                                        "status": status.HTTP_400_BAD_REQUEST,
                                        "message": "Discount coupon is not valid",
                                    }
                                )
                        can_apply_discount = True
                    elif OTHERS in applied_on:
                        can_apply_discount = True
                    if ITEMS == apply_type:
                        custom_data["apply_type"] = ITEMS
                        can_apply_discount = True
                    if not can_apply_discount:
                        return Response(
                            {
                                "status": status.HTTP_400_BAD_REQUEST,
                                "message": "Discount coupon is not valid.",
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    discount_attributes = discount.discount_attributes.all()
                    one_time_use_discounts = discount_attributes.filter(
                        one_time_per_user=True
                    )
                    first_order_per_user = discount_attributes.filter(
                        first_order_per_user=True
                    )
                    discount_customer = discount_attributes.filter(
                        customer=request.user
                    )
                    if one_time_use_discounts.exists() and discount_customer.exists():
                        custom_data["user"] = request.user
                        if discount.is_applied:
                            return Response(
                                {
                                    "status": status.HTTP_400_BAD_REQUEST,
                                    "message": "Discount coupon is already applied / not valid.",
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    if first_order_per_user.exists():
                        order_count = (
                            Order.objects.filter(customer=request.user)
                            .filter(~Q(payment_status=CHECKOUT))
                            .count()
                        )
                        if order_count > 0:
                            return Response(
                                {
                                    "status": status.HTTP_400_BAD_REQUEST,
                                    "message": "Coupon already used.",
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    is_applied = discount.apply_discount(cart, data=custom_data)
                    if is_applied:
                        return Response(
                            {
                                "status": status.HTTP_200_OK,
                                "message": "Discount coupon added.",
                            },
                            status=status.HTTP_200_OK,
                        )
        except Exception as err:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Something went wrong.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    if request.method == "DELETE":
        data = CartDiscountSerializer(data=request.data)
        try:
            if data.is_valid():
                cart = Cart.objects.filter(
                    customer=request.user, status="ACTIVE"
                ).first()
                discount = Discount.objects.filter(
                    code=data.data["discount_code"].upper()
                ).first()
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
                return Response(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "Discount coupon removed.",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "Discount coupon not found.",
                    },
                    status=status.HTTP_200_OK,
                )

        except:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Something went wrong.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_total_cart_item(request, *args, **kwargs):
    # name = kwargs.get("name")
    data = Cart.objects.filter(customer=request.user, status="ACTIVE")

    final_items = 0
    if data:
        data = data[0]
        final_items = data.cartitem.all().count()

    if data:
        return Response(
            {
                "final_items": final_items,
                "status": status.HTTP_200_OK,
                "message": "Products count are fetched!",
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "final_items": final_items,
                "status": status.HTTP_200_OK,
                "message": "Product list is empty!",
            },
            status=status.HTTP_200_OK,
        )


def send_otp_to_store():
    try:
        # VoiceOTPsend(settings.VOICE_PHONES)
        # OTPsend(settings.PHONES)
        pass
    except Exception as err:
        logger.error(str(err))


def update_inventory(order):
    try:
        if order.payment_status == SUCCESS or order.mode_of_payment == CASH:
            if order.cart:
                carts = Cart.objects.filter(pk=order.cart.id)
            else:
                carts = None
            if carts:
                pro = carts.first().cartitem.all()
                for product in pro:
                    # Updating SellableInventory remaining items when order were placed
                    if order.customer:
                        temp_sellable_inventory = SellableInventory.objects.filter(
                            inventory=order.customer.inventory, product=product.product
                        ).first()
                        if temp_sellable_inventory:
                            temp_quantity_remaining = (
                                temp_sellable_inventory.quantity_remaining
                            )
                            temp_sellable_inventory.quantity_remaining = float(
                                temp_quantity_remaining
                            ) - float(product.quantity)
                            temp_sellable_inventory.save()
        else:
            return HttpResponse(status=400)
    except Exception as e:
        logger.error(e)


class PlaceOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):
        # name = kwargs.get("name")
        pk = int(pk)
        delivery_type = kwargs.get("delivery_type")
        delivery_type = DeliveryType.objects.filter(type=delivery_type)[0]

        # user = User.objects.filter(name=name, phone=phone)
        # if user:
        #     user = user.first()
        # else:
        #     user = User.objects.create(
        #         name=name,
        #         phone=phone
        #     )
        #     user.save()
        if pk > 0:
            cart = Cart.objects.filter(pk=pk).first()
        else:
            cart = 0
        if cart or request.user:
            try:
                with transaction.atomic():
                    if pk > 0:
                        order = Order.objects.create(
                            customer=request.user,
                            cart=cart,
                            inventory=request.user.inventory,
                        )
                        # Updating all active items to false
                        Cart.objects.filter(pk=pk)[0].cartitem.all().update(
                            is_active=False
                        )

                        # getting all orderlist as string here
                        ordercontent = Cart.objects.filter(pk=pk)[0].get_order_list()
                        order.orderlist = ordercontent
                        order.save()
                        # Total price get
                        totalprice = Cart.objects.filter(pk=pk)[0].get_total_price()
                        order.total_price = (
                            totalprice
                            + Decimal.from_float(order.delivery_charge)
                            + Decimal.from_float(order.packaging_charge)
                        )
                        # changing the status to "ORDERED"
                        Cart.objects.filter(pk=pk).update(status="ORDER_PLACED")

                        # getting the extra address field using serializer
                        content = OrderSerializer(data=request.data)
                        if content.is_valid():
                            if (
                                "payment_id" in content.data
                                and content.data["payment_id"]
                            ):
                                order.payment = Payment.objects.get(
                                    pk=int(content.data["payment_id"])
                                )
                                order.payment_status = "SUCCESS"
                            # order.save()
                    else:
                        try:
                            order = Order.objects.create(
                                customer=request.user,
                            )
                        except:
                            logger.error("Order was not created")
                        order.inventory = request.user.inventory
                        order.delivery_charge = get_delivery_charge()
                        content = OrderSerializer(data=request.data)
                        if content.is_valid():
                            orderlist = content.data["order_list"]
                            ordercontent = ""
                            for j in orderlist:
                                ordercontent += f"{str(j['product_name'])}, (Description={str(j['product_description'])}),(Quantity={str(j['product_quantity'])}),\n"

                            store_name = content.data["store_name"]
                            ordercontent += store_name
                            order.orderlist = ordercontent
                            totalprice = 0
                            order.total_price = (
                                totalprice
                                + Decimal.from_float(order.delivery_charge)
                                + Decimal.from_float(order.packaging_charge)
                            )

                    order.checkout_address = content.data["address"]
                    order.delivery_type = delivery_type
                    order.source = WEBSITE
                    order.save()

                    customer = order.customer

                    if (
                        DISCOUNT_SETTINGS.get(
                            "discount_promotional_enabled", ""
                        ).lower()
                        == "true"
                    ):
                        customer_promotional_discounts = (
                            customer.discountattributes_set.filter(
                                applied_on=CUSTOMER,
                                one_time_per_user=True,
                                attribute_type="promotional",
                            )
                        )
                        unused_discount_code = customer_promotional_discounts.filter(
                            discount__is_applied=False
                        ).exists()
                        if (
                            customer_promotional_discounts.count()
                            < int(DISCOUNT_SETTINGS.get("maximum_count", 0))
                            and not unused_discount_code
                        ):
                            discount_obj = create_promotional_discount(order, {})

                    if pk < 0:
                        orderlist = content.data["order_list"]
                        total_price = 0
                        for j in orderlist:
                            if j["product_quantity"]:
                                product_quantity = Decimal(j["product_quantity"])
                            else:
                                product_quantity = Decimal(1)

                            order_item = OrderItem.objects.create(
                                title=j["product_name"],
                                description=j["product_description"],
                                quantity=product_quantity,
                                order_id=order,
                            )
                            # total_price = product_quantity*j['product_price']
                            order_item.save()
                        order.total_price = total_price

                    try:
                        # VoiceOTPsend(settings.VOICE_PHONES)
                        # OTPsend(settings.PHONES)
                        users = Profile.objects.filter(
                            Q(inventory=request.user.inventory, role="SK")
                            | Q(role="ADMIN")
                        )
                        device_ids = []
                        for user in users:
                            device_ids.append(user.device_id)
                        message_title = "New Order"
                        message_body = "You have a new order"
                        extra_notification_kwargs = {
                            "sound": "notification.wav",
                            "android_channel_id": "hello",
                        }
                        result = push_service.notify_multiple_devices(
                            registration_ids=device_ids,
                            message_title=message_title,
                            message_body=message_body,
                            extra_notification_kwargs=extra_notification_kwargs,
                        )

                        pass
                    except Exception as err:
                        logger.error(str(err))

                    return Response(
                        {
                            "status": status.HTTP_201_CREATED,
                            "order_id": order.id,
                            "message": "Order is placed!",
                        },
                        status=status.HTTP_201_CREATED,
                    )

            except:
                return Response(
                    {
                        "msg": "Check your order correctly",
                        "status": status.HTTP_400_BAD_REQUEST,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {
                    "message": "Order is not placed",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_order(request, pk, *args, **kwargs):
    # name = kwargs.get("name")
    pk = int(pk)
    delivery_type = kwargs.get("delivery_type")
    delivery_type = DeliveryType.objects.filter(type=delivery_type)[0]

    # user = User.objects.filter(name=name, phone=phone)
    # if user:
    #     user = user.first()
    # else:
    #     user = User.objects.create(
    #         name=name,
    #         phone=phone
    #     )
    #     user.save()
    if pk > 0:
        cart = Cart.objects.filter(pk=pk).first()
    else:
        cart = 0
    if cart or request.user:
        try:
            with transaction.atomic():
                if pk > 0:
                    order = Order.objects.create(
                        customer=request.user,
                        cart=cart,
                        inventory=request.user.inventory,
                    )
                    # Updating all active items to false
                    Cart.objects.filter(pk=pk)[0].cartitem.all().update(is_active=False)

                    # getting all orderlist as string here
                    ordercontent = Cart.objects.filter(pk=pk)[0].get_order_list()
                    order.orderlist = ordercontent
                    order.save()
                    # Total price get
                    totalprice = Cart.objects.filter(pk=pk)[0].get_total_price()
                    order.total_price = (
                        totalprice
                        + Decimal.from_float(order.delivery_charge)
                        + Decimal.from_float(order.packaging_charge)
                    )
                    # changing the status to "ORDERED"
                    Cart.objects.filter(pk=pk).update(status="ORDER_PLACED")

                    # getting the extra address field using serializer
                    content = OrderSerializer(data=request.data)
                    if content.is_valid():
                        if "payment_id" in content.data and content.data["payment_id"]:
                            order.payment = Payment.objects.get(
                                pk=int(content.data["payment_id"])
                            )
                            order.payment_status = "SUCCESS"
                        # order.save()
                else:
                    try:
                        order = Order.objects.create(
                            customer=request.user,
                        )
                    except:
                        logger.error("Order was not created")
                    order.inventory = request.user.inventory
                    order.delivery_charge = get_delivery_charge()
                    content = OrderSerializer(data=request.data)
                    if content.is_valid():
                        orderlist = content.data["order_list"]
                        ordercontent = ""
                        for j in orderlist:
                            ordercontent += f"{str(j['product_name'])}, (Description={str(j['product_description'])}),(Quantity={str(j['product_quantity'])}),\n"

                        store_name = content.data["store_name"]
                        ordercontent += store_name
                        order.orderlist = ordercontent
                        totalprice = 0
                        order.total_price = (
                            totalprice
                            + Decimal.from_float(order.delivery_charge)
                            + Decimal.from_float(order.packaging_charge)
                        )

                order.checkout_address = content.data["address"]
                order.delivery_type = delivery_type
                order.source = WEBSITE
                order.save()

                customer = order.customer

                if (
                    DISCOUNT_SETTINGS.get("discount_promotional_enabled", "").lower()
                    == "true"
                ):
                    customer_promotional_discounts = (
                        customer.discountattributes_set.filter(
                            applied_on=CUSTOMER,
                            one_time_per_user=True,
                            attribute_type="promotional",
                        )
                    )
                    unused_discount_code = customer_promotional_discounts.filter(
                        discount__is_applied=False
                    ).exists()
                    if (
                        customer_promotional_discounts.count()
                        < int(DISCOUNT_SETTINGS.get("maximum_count", 0))
                        and not unused_discount_code
                    ):
                        discount_obj = create_promotional_discount(order, {})

                if pk < 0:
                    orderlist = content.data["order_list"]
                    total_price = 0
                    for j in orderlist:
                        if j["product_quantity"]:
                            product_quantity = Decimal(j["product_quantity"])
                        else:
                            product_quantity = Decimal(1)

                        order_item = OrderItem.objects.create(
                            title=j["product_name"],
                            description=j["product_description"],
                            quantity=product_quantity,
                            order_id=order,
                        )
                        # total_price = product_quantity*j['product_price']
                        order_item.save()
                    order.total_price = total_price

                try:
                    # VoiceOTPsend(settings.VOICE_PHONES)
                    # OTPsend(settings.PHONES)
                    users = Profile.objects.filter(
                        Q(inventory=request.user.inventory, role="SK") | Q(role="ADMIN")
                    )
                    device_ids = []
                    for user in users:
                        device_ids.append(user.device_id)
                    message_title = "New Order"
                    message_body = "You have a new order"
                    extra_notification_kwargs = {
                        "sound": "notification.wav",
                        "android_channel_id": "hello",
                    }
                    result = push_service.notify_multiple_devices(
                        registration_ids=device_ids,
                        message_title=message_title,
                        message_body=message_body,
                        extra_notification_kwargs=extra_notification_kwargs,
                    )

                    pass
                except Exception as err:
                    logger.error(str(err))

                return Response(
                    {
                        "status": status.HTTP_201_CREATED,
                        "order_id": order.id,
                        "message": "Order is placed!",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except:
            return Response(
                {
                    "msg": "Check your order correctly",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    else:
        return Response(
            {"message": "Order is not placed", "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )


class get_all_orders(generics.ListAPIView):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderSerializerAll
    pagination_class = OrderListPagination

    def get_queryset(self):
        order = Order.objects.filter(
            ~Q(payment_status__in=[FAILED, CHECKOUT])
        ).order_by("-id")
        if (
            order.first().id > self.kwargs["query"]
            or order.first().id < self.kwargs["query"]
        ):
            return order
        else:
            return []


@api_view(["GET"])
def get_invoice(request, **kwargs):
    order_id = kwargs["pk"]
    invoice = Invoice.objects.filter(order_id__pk=order_id).first()
    promotional_discount = {}
    if invoice:
        invoice_items = OrderItem.objects.filter(order_id__pk=order_id)
        delivery_charge = invoice.order_id.delivery_charge
        packaging_charge = invoice.order_id.packaging_charge
    else:
        invoice_items = []
        delivery_charge = 0
        packaging_charge = 0

    if invoice:
        data = InvoiceSerializer(invoice)
        item_data = OrderItemSerializer(invoice_items, many=True)
        order = invoice.order_id
        customer = order.customer
        if customer:
            promotional_discount_code = Discount.objects.filter(
                created_on__gte=order.created_on,
                is_applied=False,
                is_active=True,
                discount_attributes__applied_on=CUSTOMER,
                discount_attributes__one_time_per_user=True,
                discount_attributes__attribute_type="promotional",
                discount_attributes__customer=customer,
            )
            if promotional_discount_code.exists():
                discount = promotional_discount_code.first()
                promotional_discount["discount_code_type"] = discount.discount_code_type
                promotional_discount["value"] = discount.value
                promotional_discount["code"] = discount.code
                promotional_discount["maximum_discount"] = discount.maximum_discount
                promotional_discount[
                    "minimum_order_value"
                ] = discount.minimum_order_value
        return Response(
            {
                "data": data.data,
                "items": item_data.data,
                "final_delivery_charge": delivery_charge,
                "packaging_charge": packaging_charge,
                "promotional_discount": promotional_discount,
                "status": status.HTTP_200_OK,
                "message": "Invoice is fetched!",
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
            status=status.HTTP_200_OK,
        )


class PlaceOrderEverything(APIView):
    def post(self, request):
        data = EverythinOrderSerializer(data=request.data)
        if data.is_valid():
            try:
                with transaction.atomic():
                    delivery_type = (
                        DeliveryType.objects.filter(type="TAKE_AWAY").first().type
                    )
                    user = Profile.objects.filter(phone_number=data.data["phone"])
                    temp_inv = Inventory.objects.get(pk=data.data["inventory"])
                    new_use_temp_inv = None
                    if temp_inv.id == 1:
                        new_use_temp_inv = Inventory.objects.get(pk=1)
                    else:
                        new_use_temp_inv = temp_inv
                    if user:
                        user = user.first()
                    else:
                        # checking if phone number is valid or not
                        try:
                            if not check_phoneNumber(data.data["phone"]):
                                return Response(
                                    {
                                        "status": status.HTTP_400_BAD_REQUEST,
                                        "message": "Inavalid Phone Number !",
                                    },
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                        except Exception as e:
                            logger.error(e)

                        # extracting the last ten digits
                        phone_number = parse_number(data.data["phone"])

                        # # creating user for that old user
                        # user = Profile(
                        #     name=data.data["name"],
                        #     phone_number=phone_number,
                        #     role="C",
                        #     # address=data.data["address"],
                        #     inventory=new_use_temp_inv
                        # )
                        # user.save()
                        #
                        # # Migrating User's order to the new
                        # old_user = User.objects.filter(name=data.data["name"], phone=phone_number).first()
                        # if old_user:
                        #
                        #     # Orders for old user
                        #     orders_olduser = Order.objects.filter(user=old_user)
                        #
                        #     # Migrating old user's order to new one
                        #     for order in orders_olduser:
                        #         order.customer = user  # migrating old user to new one
                        #         order.save()

                    # Order is created
                    order = Order.objects.create(
                        customer=user,
                        inventory=temp_inv,
                        status=Status.ORDER_PLACED.value,
                    )
                    ordercontent = ""
                    address = data.data["address"]

                    order.fulfilment_address = address
                    order.delivery_charge = Decimal.from_float(
                        float(data.data["delivery_charge"])
                    )
                    order.packaging_charge = Decimal.from_float(
                        float(data.data["packaging_charge"])
                    )
                    totalprice = Decimal.from_float(
                        float(data.data["delivery_charge"])
                    ) + Decimal.from_float(float(data.data["packaging_charge"]))
                    for j in data.data["items"]:
                        totalprice = totalprice + (
                            Decimal.from_float(float(j["product_price"]))
                            * Decimal.from_float(float(j["product_quantity"]))
                        )

                        pn = str(j["product_name"]).split("(")[0]
                        pd = str(j["product_description"])
                        pq = str(j["product_quantity"])
                        pp = str(j["product_price"])
                        pu = str(j["product_unit"])
                        pe = str(j["product_expiry"])
                        pbn = str(j["product_batch_number"])
                        if len(pn) > 0 and len(pq) > 0 and len(pp) > 0:
                            ordercontent = (
                                ordercontent
                                + f"{str(pn)}, (Description={str(pd)}),(Quantity={str(pq)} ), (Unit={str(pu)})\n"
                            )

                        # Removing selleble item
                        temp_sellable_inventory = SellableInventory.objects.filter(
                            inventory_id=int(data.data["inventory"]),
                            product=j["product_id"],
                            expiry=pe,
                            batch_number=pbn,
                        ).first()
                        if temp_sellable_inventory:
                            temp_quantity_remaining = (
                                temp_sellable_inventory.quantity_remaining
                            )
                            temp_sellable_inventory.quantity_remaining = float(
                                temp_quantity_remaining
                            ) - float(j["product_quantity"])
                            temp_sellable_inventory.save()

                    order.orderlist = ordercontent
                    order.fulfilment_type = delivery_type
                    order.total_price = totalprice
                    order.source = BILLING

                    # Creating Job scheduler when there is a schedule time for a job
                    if data.data["schedule_time"]:
                        schedule_time_temp = make_aware(
                            datetime.strptime(
                                data.data["schedule_time"], "%Y-%m-%dT%H:%M"
                            )
                        )
                        order.created_on = schedule_time_temp  # Given order time by user to create order.

                        order_id_content = Order.objects.filter(
                            pk=order.id
                        ).first()  # Order id
                        scheduler = OrderScheduler.objects.create(
                            order_id=order_id_content,
                            schedule_time=schedule_time_temp,
                        )  # Created a schedule for OTP

                    # Creating Payment object
                    payment = Payment.objects.create()

                    # Updating Payment Details
                    payment.status = PENDING
                    payment.amount = order.total_price
                    payment.source = order.source
                    payment.mode = CASH

                    # Updating Order Details
                    order.payment_status = PENDING
                    order.mode_of_payment = CASH

                    # Linking Payment and Order
                    payment.order = order

                    # Saving order and payment
                    order.save()
                    payment.save()

                    # Adding invoice
                    invoice = Invoice.objects.filter(order_id__pk=order.id).first()
                    if invoice:
                        for j in data.data["items"]:
                            if StockUnit.objects.filter(unit=j["product_unit"]):
                                unit = StockUnit.objects.filter(
                                    unit=j["product_unit"]
                                ).first()
                            else:
                                unit = ""
                            if Product.objects.filter(pk=j["product_id"]):
                                product = Product.objects.filter(
                                    pk=j["product_id"]
                                ).first()
                            else:
                                product = ""

                            order_item = OrderItem.objects.create(
                                product_id=product,
                                title=j["product_name"].split("(")[0],
                                description=str(j["product_description"]),
                                quantity=j["product_quantity"],
                                price=Decimal(j["product_price"])
                                * Decimal(j["product_quantity"]),
                                order_id=order,
                                final_price=Decimal(j["product_price"])
                                * Decimal(j["product_quantity"]),
                                batch_number=str(j["product_batch_number"]),
                                expiry=str(j["product_expiry"]),
                            )
                            order_item.save()
                    if settings.MESSAGE_SEND:
                        send_order_communication(order, payment)
                    # return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Order is not placed!"},
                    #                 status=status.HTTP_400_BAD_REQUEST)
                    return Response(
                        {
                            "status": status.HTTP_201_CREATED,
                            "message": "Order is placed!",
                        },
                        status=status.HTTP_201_CREATED,
                    )

            except Exception as err:
                return Response(
                    {"message": str(err), "status": status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )


#  For adding everything order from frontend.


@api_view(["GET"])
def user_search(request, *args, **kwargs):
    query = kwargs.get("query")
    search = (
        Profile.objects.filter(phone_number__contains=query)
        .order_by()
        .values("phone_number", "name")
        .distinct()
    )
    search2 = (
        User.objects.search(query=query).order_by().values("phone", "name").distinct()
    )

    serializer1 = ProfileSerializer(search, many=True)
    serializer2 = UserSerializer(search2, many=True)

    if serializer1 or serializer2:
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Search fetched!",
                "data": serializer1.data + serializer2.data,
            },
            status=status.HTTP_200_OK,
        )

    else:
        return Response(
            {
                "message": "Search result not found",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def product_search(request, *args, **kwargs):
    inv = request.GET.get("inv")
    # name = request.GET.get("name")
    # search = Product.objects.filter(is_active_product=True).order_by().distinct()
    # serializer = ProductMiniSerializer(search, many=True)
    final = arrange_data(inv)
    if final is not None:
        return Response({"results": final}, status=status.HTTP_200_OK)
    else:
        return Response(
            {
                "message": "Search result not found",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def stocking_product_search(request, *args, **kwargs):
    inv = request.GET.get("inv")
    # name = request.GET.get("name")
    # search = Product.objects.filter(is_active_product=True).order_by().distinct()
    # serializer = ProductMiniSerializer(search, many=True)
    final = arrange_stocking_data(inv)
    if final is not None:
        return Response({"results": final}, status=status.HTTP_200_OK)
    else:
        return Response(
            {
                "message": "Search result not found",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sellable_product_search(request, *args, **kwargs):
    query = kwargs.get("query")
    paginator = PageNumberPagination()
    product_id_list = Products_search_sellable(
        request.user.inventory.id, EXTERNAL, query
    )
    product_list = SellableInventory.objects.filter(pk__in=product_id_list).order_by(
        "-updated_on"
    )

    context = paginator.paginate_queryset(product_list, request)
    serializer = SellableInventorySerializer(
        context, many=True, context={"request": request}
    )

    if product_list:
        final_response = []
        for data in serializer.data:
            temp = dict(data["product"])
            temp["quantity_remaining"] = data["quantity_remaining"]
            final_response.append(temp)

        return paginator.get_paginated_response(final_response)
    else:
        return Response(
            {
                "data": [],
                "status": status.HTTP_200_OK,
                "message": "Search result is empty!",
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def stock_dropdown_details(request, *args, **kwargs):
    added_by = Profile.objects.filter(is_superuser=True)
    stock_units = StockUnit.objects.all()
    # stock_products = Product.objects.filter(is_active_product=True)
    inventory = Inventory.objects.all()

    added_by_serial = ProfileSerializer(added_by, many=True)
    stock_units_serial = StockUnitSerializer(stock_units, many=True)
    # stock_products_serial = ProductStockSerializer(stock_products, many=True)
    inventory_serial = InventorySerializer(inventory, many=True)
    channels = Channel.objects.filter(is_active=1).only("id", "name")
    channel_serializer = ChannelSerializer(channels, many=True)

    if added_by_serial or stock_units_serial or inventory_serial:
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "List fetched!",
                "added_by": added_by_serial.data,
                "stock_unit": stock_units_serial.data,
                "inventory": inventory_serial.data,
                "channel": channel_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    else:
        return Response(
            {"message": "No data", "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )


def create_stock_object(stock_obj_data):
    try:
        return Stock.objects.create(**stock_obj_data)
    except:
        return Stock.objects.none()


@api_view(["POST"])
def add_stock(request, *args, **kwargs):
    stock_serializer = CreateStockSerializer(data=request.data)
    if stock_serializer.is_valid():
        try:
            with transaction.atomic():
                stock_data = stock_serializer.data
                for data_dict in stock_data.get("data"):
                    product = Product.objects.get(pk=data_dict["stock_product"])

                    proudct_with_this_barcode = None
                    # if "barcode" in data_dict:

                    # proudct_with_this_barcode = Product.objects.filter(is_active_product=True).filter(barcode=data_dict["barcode"])
                    # barcode = product.barcode

                    # mapping a new barcode to product with no barcode.

                    # if not barcode and not proudct_with_this_barcode and data_dict["barcode"] is not None:
                    #     product.barcode = data_dict["barcode"]
                    #     product.save()

                    profile = Profile.objects.get(pk=data_dict["added_by"])
                    # unit = StockUnit.objects.get(pk=data_dict["stock_unit"])
                    inventory = Inventory.objects.get(pk=data_dict["inventory"])
                    category = Category.objects.filter(
                        products__pk=data_dict["stock_product"]
                    )
                    expiry = data_dict["expiry"].split("-")
                    expiry_month = int(expiry[1])
                    expiry_year = int(expiry[0])
                    expiry_date = calendar.monthrange(expiry_year, expiry_month)[1]
                    expiry_datetime_obj = date(expiry_year, expiry_month, expiry_date)
                    batch_number = data_dict["batch_number"]
                    mrp = data_dict["mrp"]
                    for c in category:
                        if c.name.lower() == "external":
                            category = c.name
                        else:
                            category = c.name
                    stock_quantity = float(data_dict.get("stock_quantity"))
                    stock_obj = {
                        "user": profile,
                        "quantity": data_dict["stock_quantity"],
                        "product": product,
                        "inventory": inventory,
                        "hsn_code": data_dict["hsn_code"],
                        "purchase_trade_rate": data_dict["purchase_trade_rate"],
                        "channel_id": int(data_dict["channel"]),
                        "expiry": expiry_datetime_obj,
                        "batch_number": batch_number,
                        "net_rate": data_dict["net_rate"],
                        "discount": data_dict["discount"],
                        "gst": data_dict["gst"],
                        "procurement_price_per_product": data_dict[
                            "procurement_price_per_product"
                        ]
                        or None,
                        "channel_invoice_date": data_dict["channel_invoice_date"],
                        "channel_invoice_number": data_dict["channel_invoice_number"],
                    }
                    stock = create_stock_object(stock_obj)
                    if category and (category or "").lower() == "external":
                        pass
                    else:
                        sellable_inventory = SellableInventory.objects.filter(
                            inventory_id=inventory.id,
                            product_id=product.id,
                            expiry=expiry_datetime_obj,
                            batch_number=batch_number,
                        ).first()

                        if sellable_inventory:
                            sellable_inventory.quantity_remaining += stock_quantity
                            sellable_inventory.save(
                                update_fields=["quantity_remaining"]
                            )

                        else:
                            sellable_inventory = SellableInventory.objects.create(
                                inventory=inventory,
                                product=product,
                                quantity_remaining=stock_quantity,
                                expiry=expiry_datetime_obj,
                                batch_number=batch_number,
                            )
                        sellable_inventory.add_price(mrp, None)
                return Response(
                    {
                        "status": status.HTTP_201_CREATED,
                        "message": "Stock updated successfully!",
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as err:
            return Response(
                {"message": str(err), "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        return Response(
            {"message": stock_serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def add_stockunit(request, *args, **kwargs):
    data = StockUnitFullSerializer(data=request.data)
    if data.is_valid():
        stock = StockUnit.objects.create(
            unit=data.data["unit"], unit_description=data.data["unit_description"]
        )
        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "message": "StockUnit updated successfully!",
            },
            status=status.HTTP_201_CREATED,
        )

    else:
        return Response(
            {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def add_inventory(request, *args, **kwargs):
    tenant_obj = Tenant.objects.get(id=request.tenant_id)
    request.data["tenant"] = tenant_obj.id
    data = InventoryFullSerializer(data=request.data)
    if data.is_valid():
        inventory = Inventory.objects.create(
            name=data.data["name"],
            address=data.data["address"],
            code=data.data["code"],
            pincode=data.data["pincode"],
            longitude=data.data["longitude"],
            latitude=data.data["latitude"],
            is_active=data.data["is_active"],
            tenant=tenant_obj,
        )

        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "message": "Inventory updated successfully!",
            },
            status=status.HTTP_201_CREATED,
        )

    else:
        return Response(
            {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def add_product(request, *args, **kwargs):
    data = ProductFullSerializer(data=request.data)
    if data.is_valid():

        temp_barcode = data.data["barcode"]
        if temp_barcode:
            product = Product.objects.filter(is_active_product=True).filter(
                barcode=temp_barcode
            )
            if product:
                return Response(
                    {
                        "message": "Product already exists with this barcode",
                        "status": status.HTTP_400_BAD_REQUEST,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        temp_category = None
        if data.data["category"]:
            temp_category = Category.objects.get(pk=data.data["category"])
        product = Product.objects.create(
            product_name=data.data["product_name"],
            price=data.data["price"],
            category=temp_category,
            description=data.data["description"],
            sku=data.data["sku"],
            photo=data.data["photo"],
            barcode=data.data["barcode"],
        )
        category_mapping_data = data.data["categories"]
        if category_mapping_data:
            for category_id in category_mapping_data:
                try:
                    category_to_map = Category.objects.get(pk=category_id)
                    if category_to_map:
                        category_to_map.products.add(product.id)
                except:
                    continue
        search = Product.objects.filter(pk=product.id)
        data = ProductMiniSerializer(search, many=True)
        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "message": "Product updated successfully!",
                "data": data.data,
            },
            status=status.HTTP_201_CREATED,
        )

    else:
        return Response(
            {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )


# for image upload
# class PostView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def get(self, request, *args, **kwargs):
#         wasted_product = WastedProduct.objects.all()
#         serializer = WastedProductSerializer(wasted_product, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         # import ipdb; ipdb.set_trace()
#         wasted_product_serializer = WastedProductSerializer(data=request.data)
#         print(wasted_product_serializer)
#         print(wasted_product_serializer.data)
#         if wasted_product_serializer.is_valid():
#             return Response(wasted_product_serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             print('error', wasted_product_serializer.errors)
#             return Response(wasted_product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# for posting wasted product
@parser_classes((MultiPartParser, FormParser))
@api_view(["POST"])
def add_wasted_product(request, *args, **kwargs):
    data = WastedProductSerializer(data=request.data)

    if data.is_valid():
        temp_category = None
        if data.data["category"]:
            temp_category = Category.objects.get(pk=data.data["category"])
        product = Product.objects.create(
            product_name=data.data["product_name"],
            price=data.data["price"],
            category=temp_category,
            description=data.data["description"],
            sku=data.data["sku"],
            photo=data.data["photo"],
        )
        return Response(
            {
                "status": status.HTTP_201_CREATED,
                "message": "Product updated successfully!",
            },
            status=status.HTTP_201_CREATED,
        )

    else:
        return Response(
            {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST,
        )



class StockunitsView(APIView):
    def get(self, request):
            stock_unit = Stock.objects.filter(tenant=request.tenant_id).values_list(
                "pk", flat=True
            )
            if stock_unit:
                units = StockUnit.objects.filter(id__in=stock_unit)
                if units:
                    data = StockUnitSerializer(units, many=True)
                    return Response(
                        {
                            "data": data.data,
                            "status": status.HTTP_200_OK,
                            "message": "Units are fetched!",
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(
                    {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                    status=status.HTTP_200_OK,
                )

    def post(self, request):
        data = StockUnitFullSerializer(data=request.data)
        if data.is_valid():
            stock = StockUnit.objects.create(
                unit=data.data["unit"], unit_description=data.data["unit_description"]
            )
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "StockUnit updated successfully!",
                },
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
def get_mini_product(request, **kwargs):
    product_id = kwargs.get("id")
    qs = get_object_or_404(Product, tenant=request.tenant_id, pk=product_id)
    serializer = ProductSerializer(qs, many=False)
    if qs:
        return Response(
            {"data": serializer.data, "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "data": "Product result not found :-( ",
                "status": status.HTTP_404_NOT_FOUND,
            },
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET", "DELETE"])
# @permission_classes([IsAuthenticated])
def favouriteProductview(request, **kwargs):
    if request.method == "GET":
        response = {}
        product = Product.objects.filter(tenant=request.tenant_id).values_list(
            "pk", flat=True
        )
        fav = FavouriteProduct.objects.filter(
            user_id=request.user.id, product_id__in=product
        )
        serializer = FavouriteProductSerializer(
            fav, many=True, context={"request": request}
        )
        if serializer.data:
            response["data"] = serializer.data
            response["status"] = status.HTTP_200_OK
            response["msg"] = "Favourite Success"
        else:
            response["status"] = status.HTTP_200_OK
            response["msg"] = "Favourite products not found"
        return Response(response, status=response["status"])

    if request.method == "DELETE":
        response = {}
        serializer = FavouriteProductSerializerMin(data=request.data)
        if serializer.is_valid():
            product = Product.objects.filter(
                pk=serializer.data["product_id"], tenant=request.tenant_id
            ).first()
            FavouriteProduct.objects.filter(
                user_id=request.user, product_id=product
            ).delete()
            response["status"] = status.HTTP_200_OK
            response["msg"] = "Favourite delete success"
            return Response(response, status=response["status"])
        else:
            return Response(
                {"data": serializer.errors, "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addfavouriteProductview(request, **kwargs):
    if request.method == "POST":
        response = {}
        serializer = FavouriteProductSerializerMin(data=request.data)
        if serializer.is_valid():
            product = Product.objects.filter(pk=serializer.data["product_id"]).first()
            FavouriteProduct.objects.create(user_id=request.user, product_id=product)
            response["data"] = serializer.data
            response["status"] = status.HTTP_201_CREATED
            response["msg"] = "Favourite Added!"
            return Response(response, status=response["status"])
        else:
            return Response(
                {"data": serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RecentOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        pagination_class = RecentOrderPagination
        paginator = pagination_class()
        response = {}
        recent_orders = Order.objects.filter(customer=request.user).order_by(
            "-created_on"
        )
        page = paginator.paginate_queryset(recent_orders, request)
        serializer = RecentOrderSerializer(page, many=True)
        customer = request.user
        promotional_discount = {}
        if customer:
            promotional_discount_code = Discount.objects.filter(
                is_applied=False,
                is_active=True,
                discount_attributes__applied_on=CUSTOMER,
                discount_attributes__one_time_per_user=True,
                discount_attributes__attribute_type="promotional",
                discount_attributes__customer=customer,
            )
            if promotional_discount_code.exists():
                discount = promotional_discount_code.first()
                promotional_discount["discount_code_type"] = discount.discount_code_type
                promotional_discount["value"] = discount.value
                promotional_discount["code"] = discount.code
                promotional_discount["maximum_discount"] = discount.maximum_discount
                promotional_discount[
                    "minimum_order_value"
                ] = discount.minimum_order_value
        response["data"] = serializer.data
        response["promotional_discount"] = promotional_discount
        response["total_pages"] = paginator.page.paginator.num_pages
        if serializer.data:
            response["status"] = status.HTTP_200_OK
            response["msg"] = "Recent Order Success"
        else:
            response["status"] = status.HTTP_404_NOT_FOUND
            response["msg"] = "Recent Order Not Found"
        return Response(response, status=response["status"])


class Discountview(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DiscountSerializer

    def get_queryset(self):
        from datetime import datetime

        user = self.request.user
        discounts = Discount.objects.filter(
            tenant=self.request.tenant_id, is_active=True, is_applied=False
        ).filter(Q(end_time__gte=datetime.now()) | Q(end_time__isnull=True))
        results = discounts.filter(
            Q(discount_attributes__customer__id=user.id)
            | Q(discount_attributes__customer__isnull=True)
        ).filter(
            Q(discount_attributes__inventory__isnull=True)
            | Q(discount_attributes__inventory=user.inventory)
        )
        return results


class OffersView(generics.ListAPIView):
    queryset = Offers.objects.all().order_by("priority")
    serializer_class = OffersSerializer

    def list(self, request):
        queryset = Offers.objects.filter(tenant=request.tenant_id).order_by("priority")
        serializer = OffersSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def InventoryView(request):
    queryset = Inventory.objects.all().filter(tenant_id=request.tenant_id)
    if not queryset:
        return Response(
            {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
            status=status.HTTP_200_OK,
        )
    serializer = InventorySerializer(queryset, many=True)
    return Response(serializer.data)

    def post(self, request):
        tenant_obj = Tenant.objects.get(id=request.tenant_id)
        request.data["tenant"] = tenant_obj.id
        data = InventoryFullSerializer(data=request.data)


class PrescriptionReUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [
        CamelCaseRenderer,
    ]
    parser_classes = [MultiPartParser, SnakeCaseParser]

    def post(self, request, *args, **kwargs):
        serializer = PrescriptionUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = request.user
                pk = self.kwargs.get("order_id")
                order_obj = Order.objects.filter(id=pk, customer=user).first()
                if order_obj:
                    file_obj = request.FILES.get("media", "")
                    new_state = {
                        "action": request.POST.get("action"),
                        "state_type": request.POST.get("state_type"),
                        "sender": request.POST.get("sender"),
                        "created_on": datetime.now().strftime("%B %Y, %H:%M%p"),
                        "body": json.loads(request.POST.get("body")),
                    }
                    user = request.user
                    file_directory_within_bucket = "{userid}".format(userid=user.id)
                    file_path_within_bucket = os.path.join(
                        file_directory_within_bucket, file_obj.name
                    )
                    media_storage = MediaStorage()
                    media_storage.save(file_path_within_bucket, file_obj)
                    file_url = media_storage.url(file_path_within_bucket)

                    new_state["body"]["value"] = file_url

                    next_state_if_any = order_obj.append_state(new_state)
                    return JsonResponse(
                        {
                            "message": "OK",
                            "file_url": file_url,
                            "file_name": file_obj.name,
                            "order_id": order_obj.id,
                            "next_state": next_state_if_any,
                        }
                    )
                else:
                    return JsonResponse(
                        {
                            "message": "Invalid order",
                        },
                        status=400,
                    )
            except Exception as e:
                return JsonResponse(
                    {
                        "message": str(e),
                    },
                    status=400,
                )

        else:
            return JsonResponse(
                {
                    "message": serializer.errors,
                },
                status=400,
            )


class PrescriptionUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [
        CamelCaseRenderer,
    ]
    parser_classes = [
        MultiPartParser,
    ]

    def post(self, request, **kwargs):
        file_obj = request.FILES.get("media", "")
        action = request.POST.get("action")
        new_state = {
            "action": action,
            "state_type": request.POST.get("state_type"),
            "sender": request.POST.get("sender"),
            "body": json.loads(request.POST.get("body")),
            "created_on": datetime.now().strftime("%B %Y, %H:%M%p"),
        }
        user = request.user
        serializer = PrescriptionUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                file_directory_within_bucket = "{userid}".format(userid=user.id)
                file_path_within_bucket = os.path.join(
                    file_directory_within_bucket, file_obj.name
                )
                media_storage = MediaStorage()
                media_storage.save(file_path_within_bucket, file_obj)
                file_url = media_storage.url(file_path_within_bucket)
                order_obj = Order.objects.initialize(user)
                next_states_config = ORDER_STATE_WORKFLOW.get(action, {})
                if next_states_config:
                    next_states = next_states_config["next_states"]
                    # new_state["body"]["value"] = file_url
                    for next_state in next_states:
                        next_states_if_any = order_obj.append_state(next_state)
                    return JsonResponse(
                        {
                            "message": "OK",
                            "file_url": file_url,
                            "file_name": file_obj.name,
                            "order_id": order_obj.id,
                            "next_states": next_states_if_any,
                        }
                    )
            except Exception as e:
                return JsonResponse(
                    {
                        "message": str(e),
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "message": serializer.errors,
                },
                status=400,
            )


from phurti.commons.camelSnakeCaseTransformer.mixins import ToCamelCase


class StateActionView(ToCamelCase, generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = [
        MultiPartParser,
    ]
    pagination_class = OrderListPagination

    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "OK", "order_id": 1, "next_states": {}})

    def post(self, request, *args, **kwargs):
        user = request.user
        order = user.get_active_order()
        serializer = StateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                media = request.FILES.get("media", "")
                action = request.POST.get("action")
                state = {
                    "media": media,
                    "action": action,
                    "state_type": request.POST.get("state_type"),
                    "sender": request.POST.get("sender"),
                    "body": json.loads(request.POST.get("body")),
                    "created_on": datetime.now().strftime("%B %Y, %H:%M%p"),
                }
                action_class_attr = get_action_class(action)
                action_class = action_class_attr(request, state, order)
                response = action_class.execute()
                return JsonResponse(
                    {
                        "message": "OK",
                        "order_id": action_class.order.id
                        if action_class.order
                        else None,
                        "next_states": response,
                    }
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "message": str(e),
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "message": serializer.errors,
                },
                status=400,
            )


class FetchOrders(ToCamelCase, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    response = {}
    queryset = Order.objects.all().order_by("-created_on")
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            user = self.request.user
            orders = (
                Order.objects.filter(tenant=self.request.tenant_id, customer=user)
                .filter(
                    ~Q(
                        status__in=[
                            Status.INITIALISED.value,
                            Status.INVOICE_GENERATED.value,
                        ]
                    )
                )
                .order_by("-id")
            )
            return orders
        except Exception as err:
            logger.error(str(err))
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Something went wrong.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


from rest_framework.viewsets import ModelViewSet


class OrderItemsView(ToCamelCase, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@renderer_classes([ToCamelCase])
def get_active_state(request):
    active_orders_queryset = request.user.orders.filter(
        status__in=[
            Status.ORDER_PLACED.value,
            Status.INITIALISED.value,
            Status.INVOICE_GENERATED.value,
        ]
    )
    response_obj = {"order_id": None, "state": None}
    last_active_order = active_orders_queryset.last()
    if last_active_order:
        response_obj["order_id"] = last_active_order.id
        response_obj["state"] = last_active_order.state
    else:
        response_obj["order_id"] = None
        response_obj["state"] = DEFAULT_ORDER_STATE
    return JsonResponse(response_obj, safe=False)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [ToCamelCase]

    def post(self, request, *args, **kwargs):
        try:
            order_id = request.data["order_id"]
            order_obj = Order.objects.filter(id=order_id, customer=request.user).first()
            if order_obj:
                order_obj.status = Status.CANCELLED.value
                order_obj.save()
                response_obj = {
                    "order_id": order_id,
                    "status": Status.CANCELLED.value,
                    "message": "OK",
                }
                return Response(response_obj, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmOrderView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [ToCamelCase]

    def post(self, request, *args, **kwargs):
        try:
            order_id = request.data["order_id"]
            order_obj = Order.objects.filter(id=order_id, customer=request.user).first()
            if order_obj:
                order_obj.status = Status.ORDER_PLACED.value
                order_obj.save()
                response_obj = {
                    "order_id": order_id,
                    "status": Status.ORDER_PLACED.value,
                    "message": "OK",
                }
                return JsonResponse(response_obj, safe=False)
            else:
                return Response(
                    {"message": "Invalid order"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@renderer_classes([CamelCaseRenderer])
def request_callback(request):
    try:
        user = request.user
        data = request.data
        name = user.name
        phone = user.phone_number
        active_orders_queryset = request.user.orders.filter(
            status__in=[
                Status.ORDER_PLACED.value,
                Status.INITIALISED.value,
                Status.INVOICE_GENERATED.value,
            ]
        )
        serializer = RequestCallbackSerializer(data=data)
        if serializer.is_valid():
            if active_orders_queryset:
                active_order = active_orders_queryset.last()
                next_state_if_any = ORDER_STATE_WORKFLOW.get(
                    data.get("action", None), {}
                ).get("next_state", {})
                if next_state_if_any:
                    active_order.append_state(next_state_if_any)
                    active_order.save()
            else:
                callback_obj = CallbackRequest.objects.create(name=name, phone=phone)
            response_obj = {}
            response_obj["message"] = "OK"
            response_obj["next_state"] = ORDER_STATE_WORKFLOW.get(
                data.get("action", None), {}
            ).get("next_state", {})
            return JsonResponse(response_obj, safe=False)
        else:
            return JsonResponse(
                {
                    "message": serializer.errors,
                },
                status=400,
            )
    except Exception as e:
        return JsonResponse({"message", e}, status=400, safe=False)


class OrderViewSet(viewsets.ModelViewSet):
    """Order details using id"""

    serializer_class = OrderSerializerAll
    # permission_classes = [IsAuthenticated]

    def list(self, request):
        id = request.GET.get("id")
        queryset = Order.objects.filter(pk=id)
        if queryset.exists():
            serializer = OrderSerializerAll(queryset.first(), many=False)
            return Response(serializer.data)
        else:
            return Response({"message": "Order id not found"})

    def create(self, request):
        try:
            id = request.GET.get("id")

            data = request.data
            order_items = data["items"]
            order = Order.objects.get(pk=id)
            new_orderItem = []
            final_price = order.total_price
            error = None
            for item in order_items:
                if "order_id" in item:
                    final_price += Decimal(item["price"]) * Decimal(item["quantity"])
                    orderItem = OrderItem.objects.get(
                        product_id=item["product_id"], order_id=order
                    )
                    error = self.update_sellableinventory_product_stock_orderitem(
                        float(orderItem.quantity), float(item["quantity"]), orderItem
                    )
                    print(error, orderItem)
                    if error:
                        return error
                    orderItem.price = item["price"]
                    orderItem.quantity = item["quantity"]
                    orderItem.final_price = final_price

                    orderItem.save()
                else:
                    product = Product.objects.filter(id=item["id"]).first()
                    if product:
                        try:
                            price_from_inv = product.product.current_price_variation(
                                request.user.inventory_id
                            )
                        except Exception as err:
                            logger.error(err)
                            price_from_inv = product

                        temp_price = Decimal(item["quantity"]) * Decimal(item["price"])
                        if price_from_inv:
                            temp_price = (
                                Decimal(item["quantity"]) * price_from_inv.price
                            )

                        orderItem = OrderItem(
                            title=product.product_name,
                            description=product.description,
                            product_id=product,
                            quantity=item["quantity"],
                            price=item["price"],
                            order_id=order,
                            final_price=temp_price,
                        )
                        new_orderItem.append(orderItem)
                        error = self.update_sellableinventory_product_stock_orderitem(
                            float(0), float(item["quantity"]), orderItem
                        )
                        if error:
                            return error
                        final_price += temp_price
            if new_orderItem:
                OrderItem.objects.bulk_create(new_orderItem)

            order.total_price = final_price
            order.status = Status.INVOICE_GENERATED.value
            order.save()
            return Response({"data": {"message": True}})
        except Exception as e:
            return Response(e.errors)

    def update_sellableinventory_product_stock_orderitem(
        self, previous_quantity, present_quantity, orderitem
    ):
        if orderitem.order_id.inventory:
            recaptured_stock = SellableInventory.objects.filter(
                inventory=orderitem.order_id.inventory
            ).filter(product=orderitem.product_id)
            if recaptured_stock:
                recaptured_stock = recaptured_stock.first()
                if recaptured_stock.quantity_remaining >= present_quantity:
                    if recaptured_stock.quantity_remaining > previous_quantity:

                        recaptured_stock.quantity_remaining += previous_quantity
                        recaptured_stock.quantity_remaining -= present_quantity
                        recaptured_stock.save()
                else:
                    return Response(
                        {"message": "Not enough stocks"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )


class HsnCodesViewSet(viewsets.ModelViewSet):
    """HSN Code details."""

    queryset = HsnCodes.objects.filter(active=True)
    serializer_class = HSNCodesSerializer


from scripts.get_detail import *

get_subcategory_detail()
# get_order_data()
# get_filter_product()
# get_unique_product()
# get_time_diff()

# from scripts.get_products import *
# get_product()

# from .cron import create_subs_order
# create_subs_order()
