from base import django_env

django_env()

from collections import defaultdict
from shop.models import *
import pandas as pd

invs = Inventory.objects.all()
final = defaultdict(list)
for inventory in invs:
    sellable_inv = SellableInventory.objects.filter(inventory=inventory)
    final[inventory.id] = []
    for product in sellable_inv:
        final[inventory.id].append(
            [
                product.product.product_name,
                product.product.description,
                product.quantity_remaining,
            ]
        )
    print("done for", inventory.id)

df1 = pd.DataFrame(
    final[1], columns=["Product Name", "Description", "Quantity Remaining"]
)
df2 = pd.DataFrame(
    final[8], columns=["Product Name", "Description", "Quantity Remaining"]
)
df3 = pd.DataFrame(
    final[5], columns=["Product Name", "Description", "Quantity Remaining"]
)

with pd.ExcelWriter("qunatity_remaining.xlsx.xlsx") as writer:
    df1.to_excel(writer, sheet_name="Old Whitefield")
    df2.to_excel(writer, sheet_name="Whitefield")
    df3.to_excel(writer, sheet_name="Kormangla")
