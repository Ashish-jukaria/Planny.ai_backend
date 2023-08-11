from base import django_env

django_env()

from phurti.data.utils import *
from shop.models import OrderItem

# inv last_days ilike_product_name ilike_description forecast
# query = f"SELECT DISTINCT \
#         shop_orderitem.id \
#         FROM shop_orderitem \
#         WHERE \
#         shop_orderitem.order_id.inventory.id={inventory_id}\
#         AND \
#         shop_orderitem.created_on \
#         BETWEEN {start_date} AND {end_date}\
#         AND shop_orderitem.title \
#         ILIKE \
#         '%{product_name}%'\
#         AND shop_orderitem.description    \
#         ILIKE \
#         '%{product_description}%';"

# obtained_result = execute_query_with_description(query)
# return obtained_result
import sys


def forecasting():
    import datetime

    inventory_id = sys.argv[1]
    print(sys.argv[1])
    inventory_id, last_days, forecasting_days = sys.argv[1], sys.argv[2], sys.argv[5]
    product_description = sys.argv[4]
    product_name = sys.argv[3]
    if product_description == "-":
        product_description = ""
    elif product_name == "-":
        product_name = ""

    # last_days = sys.argv[1]
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=int(last_days))

    order_item = OrderItem.objects.filter(
        order_id__inventory_id=inventory_id,
        created_on__lte=end_date,
        created_on__gte=start_date,
    )
    if product_name:
        order_item.filter(title__icontains=product_name)
    if product_description:
        order_item.filter(description__icontains=product_description)

    # title description quantity sell_count forcasting_days/sell_count price
    res = {}
    for item in order_item:
        if item.product_id:
            if item.product_id.id not in res:
                res[item.product_id.id] = {
                    "Name": item.title,
                    "Description": item.description,
                    "Sell Count": item.quantity,
                    "Price": item.price,
                }
            else:
                res[item.product_id.id]["Sell Count"] += item.quantity

    # forecast =
    for product in res:
        res[product]["Forecast Count"] = (
            res[product]["Sell Count"] // int(last_days)
        ) * int(forecasting_days)

    print("product count", len(res))
    import pandas as pd

    df = pd.DataFrame(res)
    df_transposed = df.T
    df_transposed.to_excel("forecast.xlsx")


if __name__ == "__main__":
    forecasting()
