from django.urls import path
from .views import *

urlpatterns = [
    path("items/", get_item_list, name="get_item_list"),
]
