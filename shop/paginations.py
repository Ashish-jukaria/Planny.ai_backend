from django.db.models import query
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from .models import *


class OrderListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )


class RecentOrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class LargeResultsSetPagination(LimitOffsetPagination):
    page_size = 1000
    page_size_query_param = "page_size"
    max_page_size = 10000


class StandardResultsSetPagination(LimitOffsetPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class SmallResultsSetPagination(LimitOffsetPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000
