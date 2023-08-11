from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.utils import CheckTenant
from dashboard.serializers import VariationOptionsSerializer
from rest_framework.permissions import IsAuthenticated
from shop.constants import *
from phurti.constants import *
from shop.serializers import (
    ProductCategorySerializer,
    ProductFullSerializer,
    MiniCategorySerializer,
    ProductMiniSerializer,
    CategorySerializer,
    DiscountSerializer,
    StockUnitSerializer,
    MiniProductSerializer,
    GETStocksSerializer,
    StocksSerializer,
    SellableInventoriesSerializer,
    SellableInventorySerializer,
    InventoryFullSerializer,
    InventorySerializer,
    OrderSerializer,
    DashboardOrderSerializer,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from shop.utils import fetch_leaf_category
from django.db.models import F
from shop.models import (
    Product,
    Category,
    Discount,
    VariationOptions,
    StockUnit,
    VariationTypes,
    ProductPriceVariation,
    ProductVariation,
    Toppings,
    Stock,
    SellableInventory,
    Inventory,
    VariationCombos,
    Order,
)

from account.utils import *
from django.shortcuts import get_object_or_404

from .serializers import (
    VariationTypesSerializer,
    ProductPriceVariationSerializer,
    ProductVariationSerializer,
    ToppingsSerializer,
    VariationTypesSerializer,
    VariationCombosSerializer,
)
from rest_framework.permissions import IsAuthenticated
from shop.enums import Status


class VariationTypeView(APIView):
    def get(self, request):
        types = VariationTypes.objects.all()
        if types:
            serializer = VariationTypesSerializer(types, many=True)
            return Response(
                {"Data": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": "NOT FOUND", "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )


class ProductVariationView(APIView):
    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        variations = ProductVariation.objects.filter(tenant=tenant)
        if variations:
            serializer = ProductVariationSerializer(variations, many=True)
            return Response(
                {"Data": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": "NOT FOUND", "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProductVariationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Saved": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": serializer.errors, "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        product_variation = ProductVariation.objects.filter(
            tenant=tenant, id=id
        ).first()
        if not product_variation:
            return Response(
                {"Error": "Some thing went wrong", "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProductVariationSerializer(product_variation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Saved": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": serializer.errors, "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        product_variation = ProductVariation.objects.filter(
            tenant=tenant, id=id
        ).first()
        if not product_variation:
            return Response(
                {"Error": "NO SUCH RECORD EXISTS", "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        product_variation.delete()
        return Response(
            {"Message": "Deleted Successfully", "status": status.HTTP_200_OK},
            status=status.HTTP_404_NOT_FOUND,
        )


class PriceVariationView(APIView):
    def get(self, request):
        price = ProductPriceVariation.objects.all()
        if not price:
            return Response(
                {
                    "Error": "No Price Variation data found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductPriceVariationSerializer(price, many=True)
        return Response(
            {"Data": serializer.data, "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )


class VariationOptionsGet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        variation_options = VariationOptions.objects.all()
        serializer = VariationOptionsSerializer(variation_options, many=True)
        return Response(serializer.data)


class ToppingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        toppings = Toppings.objects.filter(tenant=tenant)
        if not toppings:
            return Response(
                {
                    "Error": "No Toppings data found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ToppingsSerializer(toppings, many=True)
        return Response(
            {"Data": serializer.data, "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ToppingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Saved": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": serializer.errors, "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        topping = Toppings.objects.filter(tenant=tenant, id=id).first()
        if not topping:
            return Response(
                {
                    "message": "Incorrect ID or Tenant does'nt hold any object with these ID"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ToppingsSerializer(instance=topping, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"UPDATED": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": serializer.errors, "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        topping = Toppings.objects.filter(tenant=tenant, id=id).first()
        if not topping:
            return Response(
                {
                    "message": "Incorrect ID or Tenant doesn't hold any object with these ID"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        topping.delete()
        return Response(
            {"Message": "DELETED SUCCESSFULLY", "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )


class VariationCombosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        variation_combos = VariationCombos.objects.filter(tenant=tenant)
        serializer = VariationCombosSerializer(variation_combos, many=True)
        return Response(
            {"Data": serializer.data, "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = VariationCombosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Saved": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": serializer.errors, "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        variation_combos = VariationCombos.objects.filter(tenant=tenant, id=id).first()
        if not variation_combos:
            return Response(
                {"Error": "Some thing went wrong", "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = VariationCombosSerializer(variation_combos, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Saved": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Error": serializer.errors, "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        variation_combos = VariationCombos.objects.filter(tenant=tenant, id=id).first()
        if not variation_combos:
            return Response(
                {"Error": "Some thing went wrong", "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        variation_combos.delete()
        return Response(
            {"Message": "Deleted Successfully", "status": status.HTTP_200_OK},
            status=status.HTTP_404_NOT_FOUND,
        )


class DashboardStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        stocks = Stock.objects.filter(tenant=tenant)
        if stocks:
            serializer = GETStocksSerializer(stocks, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                status=status.HTTP_200_OK,
            )

    def post(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StocksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Inventory updated successfully!",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        stock = get_object_or_404(Stock, id=id, tenant=tenant)
        serializer = StocksSerializer(instance=stock, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Updated :": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"Error :": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        stock = get_object_or_404(Stock, id=id, tenant=tenant)
        stock.delete()
        return Response(
            {
                "data": "Stock Deleted Successfully",
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class DashboardSellableInventory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        sellableinventroies = SellableInventory.objects.filter(tenant=tenant)
        if sellableinventroies:
            serializer = SellableInventorySerializer(sellableinventroies, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellableInventoriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "SellableInventory updated successfully!",
                },
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                {"message": serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        sellableinventory = get_object_or_404(SellableInventory, id=id, tenant=tenant)
        serializer = SellableInventoriesSerializer(
            instance=sellableinventory, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"Updated :": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"data": serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        sellableinventory = get_object_or_404(SellableInventory, id=id, tenant=tenant)
        sellableinventory.delete()
        return Response(
            {
                "data": "SellableInventory Deleted Successfully",
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class DashboardInventoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = Inventory.objects.filter(tenant_id=tenant)
        if not queryset:
            return Response(
                {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                status=status.HTTP_200_OK,
            )
        serializer = InventorySerializer(queryset, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = InventoryFullSerializer(data=request.data)

        if data.is_valid():
            Inventory.objects.create(
                name=data.data["name"],
                address=data.data["address"],
                code=data.data["code"],
                pincode=data.data["pincode"],
                longitude=data.data["longitude"],
                latitude=data.data["latitude"],
                is_active=data.data["is_active"],
                tenant=tenant,
            )

            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Inventory updated successfully!",
                },
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                {"message": data.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = Inventory.objects.filter(tenant=tenant, id=id).first()
        if not data:
            return Response(
                {"No Such Record with id ": id}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = InventoryFullSerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Updated :": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"Error :": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, id):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = Inventory.objects.filter(tenant_id=tenant, id=id).first()
        if not data:
            return Response(
                {"No Such Record with id ": id}, status=status.HTTP_404_NOT_FOUND
            )
        data.delete()
        return Response({"Deleted successfully"}, status=status.HTTP_200_OK)


class AdminProductsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductFullSerializer

    def get(self, request):
        tenant_id = CheckTenant(request)
        if not tenant_id:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        products = Product.objects.filter(tenant=tenant_id)
        serializer = ProductCategorySerializer(products, many=True)
        for product in serializer.data:
            product_id = product["id"]
            product_obj = Product.objects.get(id=product_id)
            categories = product_obj.categories.all()
            category_data = MiniCategorySerializer(categories, many=True).data
            product["category"] = category_data

        return Response(
            {"data": serializer.data, "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductFullSerializer(data=request.data)
        if serializer.is_valid():
            temp_barcode = serializer.validated_data.get("barcode")

            if temp_barcode:
                product = Product.objects.filter(is_active_product=True).filter(
                    barcode=temp_barcode
                )
                if product:
                    return Response(
                        {
                            "message": "Product already exists with this barcode",
                            "status": status.HTTP_400_BAD_REQUEST,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            active_value = request.data.get("is_active_product", "").lower()
            if active_value == "true":
                is_active_product = True
            elif active_value == "false":
                is_active_product = False
            else:
                is_active_product = True

            product = Product.objects.create(
                product_name=serializer.validated_data.get("product_name"),
                price=serializer.validated_data.get("price"),
                description=serializer.validated_data.get("description"),
                sku=serializer.validated_data.get("sku"),
                photo=request.data.get("photo"),
                barcode=serializer.validated_data.get("barcode"),
                tenant=tenant,
                is_active_product=is_active_product
                
            )
            categories = request.data.getlist(
                "category", []
            )  # get list of categories from request data
            for category_id in categories:
                category = Category.objects.filter(id=category_id).first()
                if category:
                    category.products.add(product)

            search = Product.objects.filter(pk=product.id)
            data = ProductMiniSerializer(search, many=True)
            return Response(
                {
                    "status": status.HTTP_201_CREATED,
                    "message": "Product created successfully!",
                    "data": data.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, pk):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        product = get_object_or_404(Product, tenant=tenant, pk=pk)
        serializer = MiniProductSerializer(product, data=request.data)
        if serializer.is_valid():
            temp_barcode = serializer.validated_data.get("barcode")
            if temp_barcode and temp_barcode != product.barcode:
                existing_product = (
                    Product.objects.filter(is_active_product=True)
                    .filter(barcode=temp_barcode)
                    .exclude(pk=pk)
                )
                if existing_product:
                    return Response(
                        {
                            "message": "Product already exists with this barcode",
                            "status": status.HTTP_400_BAD_REQUEST,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            product.product_name = serializer.validated_data.get(
                "product_name", product.product_name
            )
            product.price = serializer.validated_data.get("price")
            product.description = serializer.validated_data.get("description")
            product.sku = serializer.validated_data.get("sku")
            product.photo = request.FILES.get("photo", product.photo)
            product.barcode = temp_barcode
            active_value = request.data.get("is_active_product", "").lower()
            if active_value == "true":
                product.is_active_product = True
            elif active_value == "false":
                product.is_active_product = False
            else:
                product.is_active_product = product.is_active_product
            product.save()

            categories = request.POST.getlist("category", [])
            product.categories.clear()
            for category_id in categories:
                category = Category.objects.filter(id=category_id).first()
                if category:
                    category.products.add(product)

            search = Product.objects.filter(pk=product.id)
            data = ProductMiniSerializer(search, many=True)
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Product updated successfully!",
                    "data": data.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        tenant_id = CheckTenant(request)
        if not tenant_id:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        product = get_object_or_404(Product, tenant=tenant_id, pk=pk)
        product.delete()
        return Response(
            {
                "data": "Product deleted successfully",
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class AdminCategory(APIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        has_tenant = CheckTenant(request)
        if not has_tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        tenant = Category.objects.filter(tenant=has_tenant)
        if tenant == None:
            return Response(
                {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                status=status.HTTP_200_OK,
            )
        else:
            leaf = request.GET.get("leaf")
            category = Category.objects.filter(active=True, tenant=has_tenant).order_by(
                F("priority").asc(nulls_last=True)
            )
            if leaf:
                category = fetch_leaf_category(category)
            if category:
                data = CategorySerializer(category, many=True)
                return Response(
                    {
                        "data": data.data,
                        "status": status.HTTP_200_OK,
                        "message": "Categories are fetched!",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                    status=status.HTTP_200_OK,
                )

    def post(self, request, *args, **kwargs):
        has_tenant = CheckTenant(request)
        if not has_tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CategorySerializer(data=request.POST)
        if serializer.is_valid():
            active = request.data.get("active", "").lower()
            if active == "true":
                active = True
            elif active == "false":
                active = False
            else:
                active = True
            category = Category.objects.create(
                name=serializer.validated_data.get("name"),
                description=serializer.validated_data.get("description", ""),
                slug=serializer.validated_data.get("slug"),
                priority=serializer.validated_data.get("priority"),
                active=active,
                image=request.data.get("image"),
                colour=serializer.validated_data.get("colour"),
                home_page=serializer.validated_data.get("home_page", False),
                parent_id=serializer.validated_data.get("parent_id"),
                tenant=has_tenant,
            )

            serialized_category = CategorySerializer(category).data

            return Response(
                {
                    "data": serialized_category,
                    "status": status.HTTP_201_CREATED,
                    "message": "Category created successfully!",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"data": serializer.errors, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, *args, **kwargs):
        has_tenant = CheckTenant(request)
        if not has_tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        category = Category.objects.filter(
            id=kwargs.get("pk"), tenant=has_tenant
        ).first()
        if category:
            serializer = CategorySerializer(instance=category, data=request.data)
            if serializer.is_valid():
                category.name = serializer.validated_data.get("name")
                category.description = serializer.validated_data.get("description", "")
                category.slug = serializer.validated_data.get("slug")
                category.priority = serializer.validated_data.get("priority")
                active = request.data.get("active", "").lower()
                if active == "true":
                    active = True
                elif active == "false":
                    active = False
                else:
                    active = category.active
                category.active = active
                category.image = request.data.get("image")
                category.colour = serializer.validated_data.get("colour")
                category.home_page = serializer.validated_data.get("home_page", False)
                category.parent_id = serializer.validated_data.get("parent_id")
                category.save()

                serialized_category = CategorySerializer(category).data

                return Response(
                    {
                        "data": serialized_category,
                        "status": status.HTTP_200_OK,
                        "message": "Category updated successfully!",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "data": serializer.errors,
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid data!",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    "data": [],
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Category not found!",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, *args, **kwargs):
        has_tenant = CheckTenant(request)
        if not has_tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_200_OK,
            )

        category = Category.objects.filter(
            id=kwargs.get("pk"), tenant=has_tenant
        ).first()
        if category:
            category.delete()
            return Response(
                {
                    "data": [],
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "Category deleted!",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {
                    "data": [],
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Category not found!",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class DiscountDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        tenant_id = CheckTenant(request)
        if not tenant_id:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        discounts = Discount.objects.filter(tenant_id=tenant_id)
        serializer = DiscountSerializer(discounts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        tenant_id = CheckTenant(request)
        if not tenant_id:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DiscountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        tenant_id = CheckTenant(request)
        if not tenant_id:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            discount = Discount.objects.get(pk=pk, tenant_id=tenant_id)
        except Discount.DoesNotExist:
            return Response(
                {"message": "Discount didn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = DiscountSerializer(discount, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Discount  Updated": serializer.data}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        tenant_id = CheckTenant(request)
        if not tenant_id:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            discount = Discount.objects.get(pk=pk, tenant_id=tenant_id)
        except Discount.DoesNotExist:
            return Response(
                {"message": "Discount didn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        discount.delete()
        return Response(
            {"message": "Discount Deleted Successfully"},
            status=status.HTTP_200_OK,
        )


class DashboardStockunitsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        units = StockUnit.objects.all()
        if units:
            data = StockUnitSerializer(units, many=True)
            return Response(
                {
                    "data": data.data,
                    "status": status.HTTP_200_OK,
                    "message": "Units are fetched!",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"data": [], "status": status.HTTP_200_OK, "message": "Empty!"},
                status=status.HTTP_200_OK,
            )


class DashboardordersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = CheckTenant(request)
        if not tenant:
            return Response(
                {"message": "Tenant User is empty or it does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        orders = Order.objects.filter(tenant=tenant).order_by("-created_on")
        if not orders:
            return Response(
                {"message": "This tenant did'nt hold any orders"},
                status=status.HTTP_404_NOT_FOUND,
            )

        seializer = OrderSerializer(orders, many=True)

        return Response({"data": seializer.data}, status=status.HTTP_200_OK)

    def put(self, request, id):
        orderstatus = request.data["status"]
        order = Order.objects.filter(id=id).first()
        cart = order.cart
        if orderstatus == Status["CANCELLED"].name:
            for prod in cart.cartitem.all():
                sellable = SellableInventory.objects.filter(
                    product=prod.product.id
                ).first()
                sellable.quantity_remaining += float(prod.quantity)
                sellable.save()

        serializer = DashboardOrderSerializer(instance=order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Order Updated Successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": serializer.errors}, status=status.HTTP_404_NOT_FOUND
            )
