from shop.models import Product
import json
import pandas


def get_product():
    get_product_data = Product.objects.all()
    id = []
    product_name = []
    price = []
    category = []
    description = []
    sku = []

    dump_data = {}

    for i in get_product_data:
        id.append(i.id)
        product_name.append(i.product_name)
        price.append(str(i.price))
        description.append(i.description)
        sku.append(str(i.sku))
        if i.category:
            category.append(i.category.name)
        else:
            category.append("N/A")

    dump_data["Id"] = id
    dump_data["Product Name"] = product_name
    dump_data["Price"] = price
    dump_data["Category"] = category
    dump_data["Description"] = description
    dump_data["Sku"] = sku

    with open("all_products.json", "w") as data:
        json.dump(dump_data, data)

    pandas.read_json("all_products.json").to_excel("all_products.xlsx")
