from django.urls import path
from .views import *
from django.conf.urls.static import static
from rest_framework import routers

router = routers.DefaultRouter()
router.register("order_items", OrderItemsView)
router.register("order", OrderViewSet, basename="order")
router.register("hsncodes", HsnCodesViewSet, basename="hsncodes")

urlpatterns = [
    path("get_active_state", get_active_state, name="get_active_state"),
    path("state_action", StateActionView.as_view(), name="append_state"),
    path("fetch_orders", FetchOrders.as_view(), name="fetch_view"),
    path("cancel_order", CancelOrderView.as_view(), name="cancel_order"),
    path("confirm_order", ConfirmOrderView.as_view(), name="confirm_order"),
    path(
        "category/", get_all_category, name="get_all_category"
    ),  # Fetch All the category for products,
    path("fetchcategories/", get_category, name="get_category"),  # all categories.
    path(
        "products/<str:category>/<int:categoryid>/",
        get_product_list,
        name="adhocrequest",
    ),  # Fetch All the products in specific category
    path(
        "add_to_cart/", add_to_cart, name="add_to_cart"
    ),  # Add to cart for adding bulk items
    path(
        "add_to_cart_one/", add_to_cart_one, name="Add To cart one at a time"
    ),  # Add to cart for one item at a time.
    path(
        "get_cart/", get_cart, name="get_cart"
    ),  # Get users created cart and its items.
    path(
        "place_order/<pk>/<str:delivery_type>/", place_order, name="place_order"
    ),  # Order place for User using token
    path(
        "get_total_cart_item/", get_total_cart_item, name="get_total_cart_item"
    ),  # Cart items count for cart icon.
    path(
        "all_orders/<int:query>/", get_all_orders.as_view(), name="get_all_orders"
    ),  # All Order list as a page 10 at a time.
    path(
        "invoice/<pk>/", get_invoice, name="get_invoice"
    ),  # Get invoice w.r.t the users invoice id.
    path(
        "place_order_everything/",
        PlaceOrderEverything.as_view(),
        name="place_order_everything",
    ),  # Bill making api for everyting delivery
    path(
        "usersearch/<str:query>/", user_search, name="user_search"
    ),  # for searching temp user in shop/user
    path(
        "productsearch/", product_search, name="product_search"
    ),  # for searching products and invoice item.
    path(
        "stockingproductsearch/",
        stocking_product_search,
        name="stocking_product_search",
    ),
    path(
        "sellableproductsearch/<str:query>/",
        sellable_product_search,
        name="user_product_search",
    ),  # for logged in user product search
    path(
        "get/stock/dropdowndetail/",
        stock_dropdown_details,
        name="stock_dropdown_details",
    ),  # for getting all the dropdown detail in stock table
    path("post/stock/", add_stock, name="add_stock"),  # for added stock bulk.
    # path('post/wastedproduct/', add_wasted_product, name="wastedproduct"), # for added stock bulk.
    path("post/wastedproduct/", add_wasted_product, name="wastedproduct"),
    path(
        "post/stockunit/", StockunitsView.as_view(), name="add_stockunit"
    ),  # for adding stock unit post API
    path(
        "post/inventory/", add_inventory, name="add_inventory"
    ),  # for adding products (post API)
    path("post/add_product/", add_product, name="add_product"),
    path("stock/units/", StockunitsView.as_view(), name="get_units"),  # Getting stock unit data
    path(
        "get_product/<int:id>/", get_mini_product, name="get_mini_product"
    ),  # Getting Product by id
    path(
        "favourite_products/", favouriteProductview, name="favourite_products"
    ),  # Favourite Product list
    path(
        "addfavourite_products/", addfavouriteProductview, name="addfavourite_products"
    ),  # adding favourite product
    path(
        "recent_order/", RecentOrderView.as_view(), name="recentOrderView"
    ),  # Will fetch the recent orders.
    path(
        "discount/", Discountview.as_view(), name="Discount_view"
    ),  # Discount view for getting details
    path(
        "cart/discount/", add_discount, name="add_discount"
    ),  # adding and removing discount for cartitems
    path(
        "offers/", OffersView.as_view(), name="OffersView"
    ),  # list all the offers that current tenant have.
    path(
        "inventory/", InventoryView, name="InventoryView"
    ),  # list all the inventories that current tenant have.
]

urlpatterns += router.urls
