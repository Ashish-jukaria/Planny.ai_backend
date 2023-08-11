from shop.models import *
from django.db.models import Count, Max, Sum

top = (
    OrderItem.objects.filter(created_on__gte="2022-4-1")
    .values("title")
    .annotate(total_quantity=Sum("quantity"), desc=Max("description"))
    .order_by("-total_quantity")[:100]
)

res = {}

for i in top:
    res[i["title"]] = [i["desc"]]

dates = ["2022-4-%s" % i for i in range(1, 16)]
for i in range(len(dates) - 1):
    for k in res.keys():
        sum_of_quantity_sold = (
            OrderItem.objects.filter(
                created_on__gte=dates[i], created_on__lt=dates[i + 1], title=k
            )
            .values("title")
            .annotate(ans=Sum("quantity"))
        )
        if sum_of_quantity_sold:
            res[k].append(float(sum_of_quantity_sold[0]["ans"]))
        else:
            res[k].append(0)

aa = []

for i in top:
    bb = []
    bb.append(i["title"])
    bb.extend(res[i["title"]])
    aa.append(bb)

import pandas as pd

df = pd.DataFrame(aa)
df.to_excel("past_sales_data.xlsx")
