import os
from phurti.data.utils import *


def UniqueCategorys(inventory_id):
    query = f"SELECT DISTINCT category_id FROM shop_sellableinventory LEFT JOIN \
                shop_category_products ON \
                shop_category_products.product_id=shop_sellableinventory.product_id \
                WHERE shop_sellableinventory.inventory_id={inventory_id};"

    obtained_result = execute_query(query)
    final_result = [category_id[0] for category_id in obtained_result]
    return final_result


def Products_search_sellable(inventory_id, category, search_query):
    likeOrNot = "LIKE"
    DB_URL = os.environ.get("DB_URL_PRODUCTION")
    if DB_URL:
        likeOrNot = "ILIKE"
    query = f"SELECT DISTINCT \
            shop_sellableinventory.id \
            FROM shop_sellableinventory \
            LEFT JOIN \
            shop_category_products \
            ON \
            shop_category_products.product_id=shop_sellableinventory.product_id \
            LEFT JOIN \
            shop_category \
            ON \
            shop_category.id=shop_category_products.category_id \
            LEFT JOIN \
            shop_product \
            ON \
            shop_product.id=shop_sellableinventory.product_id \
            WHERE \
            shop_sellableinventory.inventory_id={inventory_id} \
            AND \
            shop_category.name!='{category}' \
            AND shop_product.is_active_product='1' \
            AND shop_category.active='1'\
            AND shop_product.product_name \
            {likeOrNot} \
            '%{search_query}%';"

    obtained_result = execute_query(query)
    final_result = [category_id[0] for category_id in obtained_result]
    return final_result


def StockUnits():
    query = "SELECT * from shop_stockunit"
    obtained_result = execute_query_with_description(query)
    return obtained_result


def Product_details():
    query = f"SELECT \
            shop_product.id, product_name, unit_id, shop_category.name, shop_product.description, is_active_description, is_active_product, shop_productpricevariation.market_price, photo, shop_productpricevariation.price, quantity_remaining, sku, shop_sellableinventory.inventory_id, shop_sellableinventory.address, shop_sellableinventory.expiry, shop_sellableinventory.batch_number, shop_productpricevariation.id AS \"pricevariation_id\"  \
            FROM \
            shop_product \
            LEFT JOIN \
            shop_sellableinventory \
            ON \
            shop_product.id = shop_sellableinventory.product_id \
            LEFT JOIN \
            shop_category_products \
            ON \
            shop_category_products.product_id=shop_product.id \
            LEFT JOIN \
            shop_category \
            ON \
            shop_category.id=shop_category_products.category_id \
            LEFT JOIN \
            shop_inventory \
            ON \
            shop_inventory.id=shop_sellableinventory.inventory_id \
            AND \
            shop_sellableinventory.product_id=shop_product.id \
            LEFT JOIN \
            shop_productpricevariation \
            ON \
            shop_productpricevariation.sellable_inventory_id=shop_sellableinventory.id \
            where shop_product.is_active_product='1';"

    obtained_result = execute_query_with_description(query)
    return obtained_result
