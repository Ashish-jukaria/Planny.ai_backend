from shop.models import *
import random
import numpy as np


def shuffler(arr, n):
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i + 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


order_array = []
orders = Order.objects.filter(delivery_type=1, delivered=0, delivery_time__isnull=1)
for order in orders:
    order_array.append(order.id)
orders.count()
shuffler(order_array, len(order_array))

shuffle_arrangement = {
    5: 9,
    6: 4,
    7: 3,
    8: 5,
    9: 9,
    10: 95,
    11: 3,
    12: 5,
    13: 9,
    14: 10,
    15: 3,
    16: 5,
    17: 9,
    18: 10,
    19: 3,
    20: 5,
    22: 9,
    25: 10,
}

within_7_minutes = 3
within_8_minutes = 5
within_9_minutes = 3
within_10_minutes = 5
within_11_minutes = 3
within_12_minutes = 5
within_13_minutes = 3
within_14_minutes = 5
within_15_minutes = 3
within_16_minutes = 5
within_17_minutes = 3
within_18_minutes = 5
within_19_minutes = 3
within_20_minutes = 5
within_22_minutes = 3
within_25_minutes = 5
