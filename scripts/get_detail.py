from shop.models import *
import json
import pandas
from django.core.files import File


def get_detail():
    get_model_data = Order.objects.all()
    dump_data = []
    for j in get_model_data:
        dump_data.append([j.id, str(j.created_on), str(j.updated_on)])

    with open("order_data.txt", "w") as data:
        json.dump(dump_data, data)


def get_order_data():
    get_model_data = Order.objects.all()
    dump_data = {}
    ss = 1
    username = []
    phone = []
    delivery = []
    payment_status = []
    address = []
    totalPrice = []
    delivered = []
    delivery_time = []
    orderlist = []
    mod = []
    pro0 = []
    pro1 = []
    pro2 = []
    pro3 = []
    pro4 = []
    pro5 = []
    pro6 = []

    for j in get_model_data:
        username.append(j.user.name)
        phone.append(j.user.phone)
        delivery.append(str(j.delivery_type))
        payment_status.append(j.payment_status)
        address.append(j.checkout_address)
        totalPrice.append(j.total_price)
        delivered.append(j.delivered)
        delivery_time.append(str(j.delivery_time))
        mod.append(j.mode_of_payment)
        orderlist.append(j.orderlist)
        if j.cart != None:
            c = 0
            l = list(j.cart.cartitem.all()) + [
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
            ]

            for p in l[:6]:
                if p == "N/A":
                    locals()["pro" + str(c)].append("N/A")
                else:
                    locals()["pro" + str(c)].append(
                        f"{str(p.product.product_name)}, (Description={str(p.product.description)}),(Quantity={str(p.quantity)} )"
                    )
                c += 1
        else:
            pro0.append("N/A")
            pro1.append("N/A")
            pro2.append("N/A")
            pro3.append("N/A")
            pro4.append("N/A")
            pro5.append("N/A")
            pro6.append("N/A")

    for j in range(len(get_model_data)):
        pro0.append("N/A")
        pro1.append("N/A")
        pro2.append("N/A")
        pro3.append("N/A")
        pro4.append("N/A")
        pro5.append("N/A")
        pro6.append("N/A")

    dump_data["Username"] = username
    dump_data["User Phone Number"] = phone
    dump_data["Delivery Type"] = delivery
    dump_data["Payment Status"] = payment_status
    dump_data["Orderlist"] = orderlist
    dump_data["Checkout Address"] = address
    dump_data["Total Price"] = totalPrice
    dump_data["Delivered"] = delivered
    dump_data["Delivery Time"] = delivery_time
    dump_data["Mode of Payment"] = mod
    dump_data["Product-0"] = pro0[: len(get_model_data)]
    dump_data["Product-1"] = pro1[: len(get_model_data)]
    dump_data["Product-2"] = pro2[: len(get_model_data)]
    dump_data["Product-3"] = pro3[: len(get_model_data)]
    dump_data["Product-4"] = pro4[: len(get_model_data)]
    dump_data["Product-5"] = pro5[: len(get_model_data)]
    dump_data["Product-6"] = pro6[: len(get_model_data)]

    with open("order.json", "w") as data:
        json.dump(dump_data, data)

    pandas.read_json("order.json").to_excel("order.xlsx")


def get_filter_product():
    get_model_data = Order.objects.all()
    dump_data = []
    count = {}
    for j in get_model_data:
        temp = {}
        temp["Phone"] = j.user.phone
        if temp not in dump_data:
            dump_data.append(temp)

        # counting product in different dictionary
        if j.user.phone in count:
            count[j.user.phone] += 1
        else:
            count[j.user.phone] = 1

    # merging two list in one phone and count
    for j in dump_data:
        j["OrderCount"] = count[j["Phone"]]

    with open("filter_order.json", "w") as data:
        json.dump(dump_data, data)

    pandas.read_json("filter_order.json").to_excel("filter_order.xlsx")


def get_unique_product():
    get_model_data = CartItem.objects.filter(is_active=False)
    data = set()
    dump_data = []
    for j in get_model_data:
        data.add(j.product.id)

    for j in data:
        temp = {}
        product = Product.objects.filter(pk=j)
        temp["Product Name"] = product.first().product_name
        temp["Product Price"] = product.first().price
        temp["Description"] = product.first().description
        dump_data.append(temp)

    everything = Order.objects.filter(delivery_type__type="EVERYTHING")

    for h in everything:
        temp = {}
        temp["Product Name"] = h.orderlist
        temp["Product Price"] = ""
        temp["Description"] = ""
        dump_data.append(temp)

    print(dump_data)
    with open("filter_product.json", "w") as data:
        json.dump(dump_data, data)

    pandas.read_json("filter_product.json").to_excel("filter_product.xlsx")


def get_time_diff():
    get_model_data = Order.objects.all()
    time = []
    username = []
    phone = []
    delivery = []
    dump_data = {}
    for j in get_model_data:
        time.append(str(j.updated_on - j.created_on))
        username.append(j.user.name)
        phone.append(j.user.phone)
        if j.delivery_time:
            delivery.append(str(j.delivery_time - j.created_on))
        else:
            delivery.append("N/A")

    dump_data["Username"] = username
    dump_data["Phone"] = phone
    dump_data["Delivery Time"] = time
    dump_data["Delivery Time (new field)"] = delivery
    with open("filter_time.json", "w") as data:
        json.dump(dump_data, data)

    pandas.read_json("filter_time.json").to_excel("filter_time.xlsx")


def get_detail_id():
    get_model_data = Order.objects.all()
    time = []
    orderid = []
    delivery_time = []
    dump_data = {}
    for j in get_model_data:
        time.append(str(j.created_on))
        orderid.append(j.id)

        if j.delivery_time:
            delivery_time.append(str(j.delivery_time))
        else:
            delivery_time.append("N/A")

    dump_data["orderid"] = orderid
    dump_data["delivery_time"] = delivery_time
    dump_data["Created On"] = time

    with open("detailid.json", "w") as data:
        json.dump(dump_data, data)

    pandas.read_json("detailid.json").to_excel("detailid.xlsx")


def product_sku_generator():
    pro = Product.objects.all().order_by("id").update(sku=None)
    temp_id = "SKU00000001"
    product_id = Product.objects.all().order_by("id")
    for j in product_id:
        j.sku = temp_id
        j.save()
        product_sku_int = int(temp_id.split("SKU")[-1])
        new_product_sku_int = product_sku_int + 1
        temp_id = "SKU00000000"[
            : len("SKU00000000") - len(str(new_product_sku_int))
        ] + str(new_product_sku_int)
        print(temp_id)
        print(j.product_name)


# #  Creating All the Subcategory Data
# def get_subcategory_detail():
#     """
#     category Structure
#     {
#       "Instant Food": {'Ready to Eat', 'ready to eat', 'Frozen ', 'Ready to eat', 'Noodles, Pasta & Soups'},
#       "Beverages": {'Healthy Drinks & Mixes', 'Tea', 'Water', 'Milk Based Drinks', 'Energy and Soft Drinks', 'Juices and Fresh Drinks', 'Soda & Mixers', 'Coffee'}
#     },
#     SubCategory Structure
#     {
#         "Ready to Eat": {2305, 1923, 2054, 2057, 2219, 1966, 691, 1587, 1333, 1336, 955, 572, 1213, 1214, 832, 1602, 1478, 2002, 1752, 1368, 2009, 2013, 1887, 1377, 2147, 997, 1009, 761, 1786, 1279}
#     }
#     """
#     def create_mapping_data():

#         category = {} #Category With subcategory as a array in it.
#         subcategory = {} #SubCategory With ProductId as a array in it.
#         mapping_category_subcategory = {}
#         df = pandas.read_excel (r'../all_products.xlsx', engine='openpyxl')
#         row_df = df.iterrows()
#         row_df2 = df.iterrows()


#         for index, row in row_df:
#             category_lower = str(row['Category']).lower().strip()
#             subcategory_lower = str(row['SubCategory']).lower().strip()
#             if (category_lower=="nan" and type(row['Category'])==float) or (subcategory_lower=="nan" and type(row['SubCategory'])==float):
#                 continue
#             if category_lower in category:
#                 if subcategory_lower not in category[category_lower]:
#                     category[category_lower].append(subcategory_lower)
#             else:
#                 category[category_lower] = [subcategory_lower]

#             mapping_category_subcategory[subcategory_lower] = category_lower

#         for index, row in row_df2:
#             subcategory_lower = str(row['SubCategory']).lower()
#             if (subcategory_lower=="nan" and type(row['SubCategory'])==float):
#                 continue
#             if subcategory_lower in subcategory:
#                 if row['ProductId'] not in subcategory[subcategory_lower]:
#                     subcategory[subcategory_lower].append(row['ProductId'])
#             else:
#                 subcategory[subcategory_lower] = [row['ProductId']]

#         with open('category.json', 'w') as data:
#             json.dump(category, data, indent = 6)
#         with open('subcategory.json', 'w') as data:
#             json.dump(subcategory, data, indent = 6)

#         with open('mapping_category_subcategory.json', 'w') as data:
#             json.dump(mapping_category_subcategory, data, indent = 6)


#     def create_new_category():
#         with open('category.json', 'r') as f:

#             data = json.load(f)
#             d = 1
#             for category in data:
#                 category = category.capitalize()
#                 try:
#                     Category.objects.get(name__iexact=category)
#                 except:
#                     category = category.lower().strip()

#                     if " " in category:
#                         image_name = category.replace(" ", "-")
#                     else:
#                         image_name = category

#                     image = File(open(f'../phurti-icon-img/{category}/{image_name}.png', 'rb'))
#                     category = category.capitalize()

#                     category_obj = Category.objects.create(name=category)
#                     category_obj.image = image
#                     category_obj.image.save(f"{image_name}.png", image)

#                 print(category, d)
#                 d+=1

#     def create_new_sub_category():
#         mapping_category_subcategory = {}
#         with open('mapping_category_subcategory.json', 'r') as f:
#             mapping_category_subcategory = json.load(f)

#         with open('subcategory.json', 'r') as f:
#             data = json.load(f)
#             d = 1
#             for subcategory in data:
#                 try:
#                     Category.objects.get(name__iexact=subcategory)
#                 except:
#                     temp_category = mapping_category_subcategory[subcategory]
#                     try:
#                         category_object = Category.objects.get(name__iexact=temp_category)
#                     except:
#                         category_object = None

#                     category = temp_category.strip()
#                     subcategory_temp = subcategory.strip()
#                     if " " in subcategory_temp:
#                         image_name = subcategory_temp.replace(" ", "-")
#                     else:
#                         image_name = subcategory_temp

#                     image = File(open(f'../phurti-icon-img/{category}/{image_name}.png', 'rb'))


#                     subcategory = subcategory.capitalize()

#                     subcategory_obj = Category.objects.create(name=subcategory, parent=category_object)
#                     subcategory_obj.image = image
#                     subcategory_obj.image.save(f"{image_name}.png", image)

#                 print(subcategory, d)
#                 d+=1

#     def add_product_to_sub_category():
#         with open('subcategory.json', 'r') as f:
#             data = json.load(f)
#             d = 1
#             for subcategory in data:
#                 subcategory_object = Category.objects.get(name__iexact=subcategory)
#                 for product_id in data[subcategory]:
#                     try:
#                         subcategory_object.products.add(product_id)
#                         print(subcategory_object)
#                     except:
#                         continue


#     # create_mapping_data()
#     # create_new_category()
#     # create_new_sub_category()
#     # add_product_to_sub_category()
#     # print(len(subcategory))


def get_subcategory_detail():
    """
    category Structure
    {
      "Instant Food": {'Ready to Eat', 'ready to eat', 'Frozen ', 'Ready to eat', 'Noodles, Pasta & Soups'},
      "Beverages": {'Healthy Drinks & Mixes', 'Tea', 'Water', 'Milk Based Drinks', 'Energy and Soft Drinks', 'Juices and Fresh Drinks', 'Soda & Mixers', 'Coffee'}
    },
    SubCategory Structure
    {
        "Ready to Eat": {2305, 1923, 2054, 2057, 2219, 1966, 691, 1587, 1333, 1336, 955, 572, 1213, 1214, 832, 1602, 1478, 2002, 1752, 1368, 2009, 2013, 1887, 1377, 2147, 997, 1009, 761, 1786, 1279}
    }
    """

    def create_mapping_data():
        category = {}  # Category With subcategory as a array in it.
        subcategory = {}  # SubCategory With ProductId as a array in it.
        mapping_category_subcategory = {}
        df = pandas.read_excel(r"../all_products.xlsx", engine="openpyxl")
        row_df = df.iterrows()
        row_df2 = df.iterrows()

        for index, row in row_df:
            category_lower = str(row["Category"]).lower().strip()
            subcategory_lower = str(row["SubCategory"]).lower().strip()
            if category_lower == "nan" and type(row["Category"]) == float:
                continue
            if category_lower in category:
                if subcategory_lower == "nan":
                    category[category_lower] = []
                elif (
                    subcategory_lower
                    and subcategory_lower not in category[category_lower]
                ):
                    category[category_lower][subcategory_lower] = []

            else:
                category[category_lower] = {subcategory_lower: []}

            mapping_category_subcategory[subcategory_lower] = category_lower

        for index, row in row_df2:
            category_lower = str(row["Category"]).lower().strip()
            subcategory_lower = str(row["SubCategory"]).lower().strip()
            if (
                category_lower
                and category_lower != "nan"
                and subcategory_lower == "nan"
            ):
                category[category_lower].append(row["ProductId"])

            elif category_lower != "nan" and subcategory_lower != "nan":
                if row["ProductId"] not in category[category_lower][subcategory_lower]:
                    category[category_lower][subcategory_lower].append(row["ProductId"])
            else:
                continue

        with open("category.json", "w") as data:
            json.dump(category, data, indent=6)
        with open("subcategory.json", "w") as data:
            json.dump(subcategory, data, indent=6)

        with open("mapping_category_subcategory.json", "w") as data:
            json.dump(mapping_category_subcategory, data, indent=6)

    def create_new_category():
        with open("category.json", "r") as f:
            data = json.load(f)
            d = 1
            for category in data:
                category = category.capitalize()
                try:
                    Category.objects.get(name__iexact=category)
                except:
                    category = category.lower().strip()

                    if " " in category:
                        image_name = category.replace(" ", "-")
                    else:
                        image_name = category

                    image = File(
                        open(f"../phurti-icon-img/{category}/{image_name}.png", "rb")
                    )
                    category = category.capitalize()

                    category_obj = Category.objects.create(name=category)
                    category_obj.image = image
                    category_obj.image.save(f"{image_name}.png", image)

                print(category, d)
                d += 1

    def create_new_sub_category():
        with open("category.json", "r") as f:
            data = json.load(f)
            d = 1
            for category in data:
                for subcategory in data[category]:
                    try:
                        category_object = Category.objects.get(name__iexact=category)
                        Category.objects.get(
                            name__iexact=subcategory, parent=category_object
                        )
                    except:
                        try:
                            category_object = Category.objects.get(
                                name__iexact=category
                            )
                        except:
                            category_object = None

                        if type(subcategory) == int:
                            continue

                        category_name = category.strip()
                        subcategory_temp = subcategory.strip()

                        if " " in subcategory_temp:
                            image_name = subcategory_temp.replace(" ", "-")
                        else:
                            image_name = subcategory_temp
                        image = File(
                            open(
                                f"../phurti-icon-img/{category_name}/{image_name}.png",
                                "rb",
                            )
                        )
                        subcategory = subcategory.capitalize()

                        subcategory_obj = Category.objects.create(
                            name=subcategory, parent=category_object
                        )
                        subcategory_obj.image = image
                        subcategory_obj.image.save(f"{image_name}.png", image)
                        print(subcategory_obj)
                    d += 1

    def add_product_to_sub_category():
        with open("category.json", "r") as f:
            data = json.load(f)
            for category in data:
                if type(data[category]) == list:
                    for productId in data[category]:
                        category_object = Category.objects.get(name__iexact=category)
                        try:
                            category_object.products.add(productId)
                        except:
                            continue
                else:
                    for subcategory in data[category]:
                        print(category, "<<--->>", subcategory)
                        try:
                            category_object = Category.objects.get(
                                name__iexact=category
                            )
                            subcategory_object = Category.objects.get(
                                name__iexact=subcategory, parent=category_object
                            )
                            for product_id in data[category][subcategory]:
                                try:
                                    subcategory_object.products.add(product_id)
                                except:
                                    continue
                        except:
                            continue

    # create_mapping_data()
    # create_new_category()
    # create_new_sub_category()
    # add_product_to_sub_category()
    # print(len(subcategory))
