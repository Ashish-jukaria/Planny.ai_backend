from base import django_env

django_env()

from shop.models import *
from django.utils import timezone


def migrate_product():
    sellable = SellableInventory.objects.all()
    for i in sellable:
        market_price = i.product.market_price
        price = i.product.price
        timeNow = timezone.now()
        ProductPriceVariation.objects.create(
            sellable_inventory=i,
            is_active=True,
            price=price,
            market_price=market_price,
            valid_from=timeNow,
        )
        print(i.product)


if __name__ == "__main__":
    migrate_product()
