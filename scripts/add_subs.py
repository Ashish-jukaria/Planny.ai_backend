from shop.models import *
from django.utils.timezone import make_aware
import json


def create_subs_remaining_order_daterange():
    today = datetime.date.today()
    tommorow = today + datetime.timedelta(days=1)

    day_count = (today - (today - datetime.timedelta(days=36))).days + 1

    main_date = today - datetime.timedelta(days=36)
    for day in range(day_count):
        active_subscription = Subscriptions.objects.filter(
            from_date__lte=main_date + datetime.timedelta(day)
        ).filter(to_date__gte=main_date + datetime.timedelta(day))
        print(main_date + datetime.timedelta(day))
        for subs in active_subscription:
            user = User.objects.filter(
                name=subs.customer.name, phone=subs.customer.phone
            ).first()
            # print()
            temp_cartitem = CartItem(
                product=subs.products.all().first(),
                quantity=Decimal("{:.4f}".format(1)),
                user=user,
                is_active=False,
            )

            orders = Order.objects.filter(
                user=user, created_on__date=main_date + datetime.timedelta(day)
            )

            for order in orders:
                if order.cart and len(order.cart.cartitem.all()) == 1:
                    for pro in order.cart.cartitem.all():
                        if pro.product == subs.products.all().first():
                            CartItem.objects.filter(pk=pro.id).update(
                                quantity=subs.quantity
                            )
                            price = (
                                order.cart.get_total_price(
                                    cartitems=order.cart.cartitem.all()
                                )
                                + order.packaging_charge
                                + order.delivery_charge
                            )
                            Order.objects.filter(pk=order.id).update(
                                orderlist=order.cart.get_order_list(),
                                total_price=price,
                            )
                            Invoice.objects.filter(order_id=order.id).update(
                                final_price=price
                            )

                            invoice_item = InvoiceItem.objects.filter(
                                invoice_id=Invoice.objects.filter(
                                    order_id=order.id
                                ).first()
                            ).update(quantity=subs.quantity)
                            print("Updated!", order.id, price)


def create_subs_order(givendate, i):
    tommorow = givendate
    createTime = datetime.datetime.combine(tommorow, i.time_slot)
    createTime = datetime.datetime.combine(tommorow, i.time_slot)
    awarecreateTime = make_aware(createTime)

    # This is for backward compatibility for creating orders for previous user's
    if i.customer:
        name = i.customer.name
        phone = i.customer.phone
        delivery_type = DeliveryType.objects.filter(type="EXPRESS").first()
        user = User.objects.filter(name=name, phone=phone)
        if user:
            user = user.first()
        else:
            user = User.objects.create(name=name, phone=phone)
            user.save()
        cart = Cart.objects.create(
            user=user,
        )
        for pro in i.products.all():
            cartitem = CartItem.objects.create(
                product=pro, user=user, quantity=i.quantity
            )
            cartitem.save()
            cart.cartitem.add(cartitem)

        cart.save()
        order = Order.objects.create(
            user=user,
            cart=cart,
        )
        # Updating all active items to false
        Cart.objects.filter(pk=cart.id).first().cartitem.all().update(is_active=False)

        # getting all orderlist as string here
        ordercontent = Cart.objects.filter(pk=cart.id).first().get_order_list()

        # Total price get
        totalprice = Cart.objects.filter(pk=cart.id).first().get_total_price()

        # changing the staus to "ORDERED"
        Cart.objects.filter(pk=cart.id).update(status="ORDER_PLACED")

        # getting the extra address field

        order.checkout_address = i.customer.address
        order.orderlist = ordercontent
        order.delivery_type = delivery_type
        order.total_price = totalprice + Decimal(10)
        order.created_on = awarecreateTime
        order.inventory = i.inventory
        order.save()

        print("Order Created succesfully")

    # for user which are created on admin's default user
    elif i.new_customer:
        customer = i.new_customer
        delivery_type = DeliveryType.objects.filter(type="EXPRESS").first()
        cart = Cart.objects.create(
            customer=customer,
        )
        for pro in i.products.all():
            cartitem = CartItem.objects.create(
                product=pro, customer=customer, quantity=i.quantity
            )
            cartitem.save()
            cart.cartitem.add(cartitem)

        cart.save()
        order = Order.objects.create(customer=customer, cart=cart)
        # Updating all active items to false
        Cart.objects.filter(pk=cart.id).first().cartitem.all().update(is_active=False)

        # getting all orderlist as string here
        ordercontent = Cart.objects.filter(pk=cart.id).first().get_order_list()

        # Total price get
        totalprice = Cart.objects.filter(pk=cart.id).first().get_total_price()

        # changing the staus to "ORDERED"
        Cart.objects.filter(pk=cart.id).update(status="ORDER_PLACED")

        # getting the extra address field

        order.checkout_address = i.new_customer.address
        order.orderlist = ordercontent
        order.delivery_type = delivery_type
        order.total_price = totalprice + Decimal(10)
        order.created_on = awarecreateTime
        order.inventory = i.inventory
        order.save()

        print("Order Created succesfully")


def punch_subs_remaining_order_daterange():
    dump_data = {}
    today = datetime.date.today()
    tommorow = today + datetime.timedelta(days=1)

    day_count = (today - (today - datetime.timedelta(days=150))).days + 1

    main_date = today - datetime.timedelta(days=150)
    for day in range(day_count):
        active_subscription = Subscriptions.objects.filter(
            from_date__lte=main_date + datetime.timedelta(day)
        ).filter(to_date__gte=main_date + datetime.timedelta(day))
        print(main_date + datetime.timedelta(day))
        dump_data[str(main_date + datetime.timedelta(day))] = []
        for subs in active_subscription:
            # print()
            if subs.customer:
                user = User.objects.filter(
                    name=subs.customer.name, phone=subs.customer.phone
                ).first()
                temp_cartitem = CartItem(
                    product=subs.products.all().first(),
                    quantity=Decimal("{:.4f}".format(1)),
                    user=user,
                    is_active=False,
                )

                orders = Order.objects.filter(
                    user__name=subs.customer.name,
                    user__phone=subs.customer.phone,
                    created_on__date=main_date + datetime.timedelta(day),
                )

            elif subs.new_customer:
                user = subs.new_customer
                temp_cartitem = CartItem(
                    product=subs.products.all().first(),
                    quantity=Decimal("{:.4f}".format(1)),
                    customer=user,
                    is_active=False,
                )

                orders = Order.objects.filter(
                    customer=user, created_on__date=main_date + datetime.timedelta(day)
                )

            if not len(orders):
                create_subs_order(main_date + datetime.timedelta(day), subs)
                if subs.customer:
                    dump_data[str(main_date + datetime.timedelta(day))].append(
                        {
                            "Customer": str(subs.customer),
                            "Product": str(subs.products.all().first()),
                        }
                    )
                    print("No Order Previously")
                    print("Product:", subs.products.all().first())
                    print("User:", subs.customer)
                    print("\n\n")
                else:
                    dump_data[str(main_date + datetime.timedelta(day))].append(
                        {
                            "Customer": str(subs.new_customer),
                            "Product": str(subs.products.all().first()),
                        }
                    )
                    print("No Order Previously")
                    print("Product:", subs.products.all().first())
                    print("User:", subs.new_customer)
                    print("\n\n")
            else:
                for order in orders:
                    if order.cart and len(order.cart.cartitem.all()) == 1:
                        for pro in order.cart.cartitem.all():
                            if pro.product != subs.products.all().first():
                                create_subs_order(
                                    main_date + datetime.timedelta(day), subs
                                )
                                if subs.customer:
                                    print(subs.customer)
                                else:
                                    print(subs.new_customer)

    with open("new_orders.json", "w") as data:
        json.dump(dump_data, data, indent=4)


## ---------- Invoice Item

# title
# description
# quantity
# price
# invoice_id
# product_id
# unit_id

## ---------- Order Item
# title
# description
# order_id
# product_id
# quantity
# price
# discount_code
# final_price


def migrate_invoice_item():
    all_invoice = Invoice.objects.all()

    for invoice in all_invoice:
        temp_invoice_item = InvoiceItem.objects.filter(invoice_id=invoice)

        for invoice_item in temp_invoice_item:
            if invoice_item.price:
                temp = invoice_item.quantity * invoice_item.price
            else:
                temp = Decimal(0)

            order_item = OrderItem.objects.create(
                title=invoice_item.title,
                description=invoice_item.description,
                order_id=invoice.order_id,
                product_id=invoice_item.product_id,
                quantity=invoice_item.quantity,
                price=invoice_item.price,
                final_price=temp,
            )

            order_item.created_on = invoice_item.created_on
            order_item.updated_on = invoice_item.updated_on
            order_item.save()

        print("Order Item created for order:", invoice.order_id)
