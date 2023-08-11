from phurti.constants import *
from rest_framework.response import Response
from rest_framework import status


class BaseGateway:
    def __init__(self, data={}, request=None, **kwargs):
        self.data = data
        self.request = request

    def get_checkout_status(self):
        return CHECKOUT

    def checkout(self, request):
        response_data = {"status": "SOME STATUS HERE"}
        return Response(response_data, status=status.HTTP_200_OK)

    def success(self, request):
        response_data = {"status": "SOME STATUS HERE"}
        return Response({"status": "success"}, status=status.HTTP_200_OK)

    def failure(self, request):
        response_data = {"status": "SOME STATUS HERE"}
        return Response({"status": "success"}, status=status.HTTP_200_OK)
