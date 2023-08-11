from django.urls import path
from .views import (
    VariationTypeView,
    PriceVariationView,
    ProductVariationView,
    ToppingsView,
    VariationCombosView,
    DashboardStockView,
    DashboardSellableInventory,
    DashboardInventoryView,
    AdminProductsView,
    AdminCategory,
    DiscountDashboardAPIView,
    DashboardStockunitsView,
    VariationOptionsGet,
    DashboardordersView
)
from shop.views import FetchOrders

urlpatterns = [
    path("variation_type/", VariationTypeView.as_view()),
    path("price_variation/", PriceVariationView.as_view()),
    path("product_variation/", ProductVariationView.as_view()),
    path("product_variation/<int:id>/", ProductVariationView.as_view()),
    path(
        "variation_options/",
        VariationOptionsGet.as_view(),
        name="variation_options",
    ),
    path("toppings/", ToppingsView.as_view()),
    path("toppings/<int:id>/", ToppingsView.as_view()),
    path("variation_combos/", VariationCombosView.as_view(), name="variation_combos"),
    path(
        "variation_combos/<int:id>/",
        VariationCombosView.as_view(),
        name="variation_combos",
    ),
    path(
        "stock/",
        DashboardStockView.as_view(),
        name="dashboard-stock",
    ),
    path(
        "stock/<int:id>/",
        DashboardStockView.as_view(),
        name="dashboard-stock",
    ),
    path(
        "sellableinventory/",
        DashboardSellableInventory.as_view(),
        name="dashboard_sellableinventory_view",
    ),
    path(
        "sellableinventory/<int:id>/",
        DashboardSellableInventory.as_view(),
        name="dashboard_sellableinventory_view",
    ),
        path(
        "inventory/",
        DashboardInventoryView.as_view(),
        name="dashboard_inventory_view",
    ),
    path(
        "inventory/<int:id>/",
        DashboardInventoryView.as_view(),
        name="dashboard_inventory_view",
    ),
    path("products/", AdminProductsView.as_view(), name="admin_product"),
    path(
        "products/<int:pk>/",
        AdminProductsView.as_view(),
        name="admin_product",
    ),
    path("categories/", AdminCategory.as_view(), name="admincategorys"),
    path(
        "categories/<int:pk>/", AdminCategory.as_view(), name="admincategorys"
    ),
    path("discounts/", DiscountDashboardAPIView.as_view(), name="discounts"),
    path(
        "discounts/<int:pk>/",
        DiscountDashboardAPIView.as_view(),
        name="discount-detail",
    ),
    path(
        "stockunits/",
        DashboardStockunitsView.as_view(),
        name="stock_units_view",
    ),

    path(
        "orders/",
        # FetchOrders.as_view(), 
        # name="fetch_view",
        DashboardordersView.as_view(),
        name="orderview"
        ),
    path(
        "orders/<int:id>/",
        DashboardordersView.as_view(),
        name="orderview"
        )
    
    
    
]
