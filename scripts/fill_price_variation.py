from base import django_env

django_env()
from shop.models import *
from django.utils import timezone


def price_variation():
    sellable_inventory_product = SellableInventory.objects.all()
    for inventory_product in sellable_inventory_product:
        price_variation = ProductPriceVariation.objects.create(
            sellable_inventory=inventory_product,
            is_active=inventory_product.is_active,
            valid_from=timezone.now(),
            price=Decimal(0),
            market_price=None,
        )
        # price_variation.price = Decimal(0)
         # price_variation.market_price = None
        if inventory_product.product and inventory_product.product.price:
            price_variation.price = inventory_product.product.price
            price_variation.market_price = inventory_product.product.market_price
            price_variation.save()
            print("DONE FOR ", inventory_product.product)
        else:
            print("not done for id", inventory_product.id)


if __name__ == "__main__":
    price_variation()
