from base import django_env

django_env()
import logging

logger = logging.getLogger("phurti")
import pandas as pd
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath("__file__"))
from shop.models import SellableInventory

import math


def fill_product_address(inventory_id):
    try:
        filepath = f"{BASE_DIR}/../address_mapping.xlsx"
        data = pd.read_excel(filepath, engine="openpyxl")
        df = pd.DataFrame(data, columns=["id", "address", "barcode"])

        for index, row in df.iterrows():
            address = f"{str(row.address)}"
            product_id = int(row.id)
            product = SellableInventory.objects.filter(
                product__pk=product_id, inventory__pk=inventory_id
            ).first()
            if product:
                if product.product and not product.product.barcode:
                    product.product.barcode = row.barcode
                    product.product.save()
                product.address = address
                product.save()
                print(product.product)

    except Exception as e:
        logger.error(str(e))
        print("UPLOAD FAILED", str(e))


if __name__ == "__main__":
    fill_product_address(2)
