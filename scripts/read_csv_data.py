from base import django_env
import os
import csv

django_env()

from shop.models import Category, Product, Inventory, SellableInventory
from account.models import Tenant, TenantCategory


def read_csv_data(file_path):
    tenant_category = TenantCategory.objects.create(name="TenantCategory1")
    tenant = Tenant.objects.create(
        title="avenger", tenant_category=tenant_category, subdomain="iron-man"
    )
    inventory = Inventory.objects.create(tenant=tenant, name="Inventory2")

    with open(file_path, "r") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row if it exists
        for row in csv_reader:
            category_name = row[1]
            product_name = row[2]
            description = row[3]
            price = float(row[4]) / 100  # Convert price to float and divide by 100

            # Check if the category already exists
            category = Category.objects.filter(name=category_name).first()

            # If the category doesn't exist, create a new one
            if not category:
                category = Category.objects.create(name=category_name, tenant=tenant)

            # Create a new product and associate it with the category
            product = Product.objects.create(
                product_name=product_name,
                description=description,
                price=price,
                tenant=tenant,
            )
            category.products.add(product)
            SellableInventory.objects.create(
                tenant=tenant,
                product=product,
                quantity_remaining=10,
                inventory=inventory,
            )

    print("CSV data saved successfully")


# Call the function with the path to your CSV file
filepath = "/home/ashish/Downloads/abc.csv"
read_csv_data(filepath)
