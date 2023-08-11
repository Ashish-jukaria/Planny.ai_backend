from payments.gateways.base import BaseGateway
from phurti.constants import *
from rest_framework.response import Response
from rest_framework import status


class OfflineGateway(BaseGateway):
    def get_payment_source(self):
        return OFFLINE

    def get_success_status(self):
        return PAYMENT_SUCCESS

    def get_failure_status(self):
        return PAYMENT_FAILED

    def success(self, request):
        response_data = {"status": "SOME STATUS HERE"}
        return Response(response_data, status=status.HTTP_200_OK)

    def failure(self, request):
        response_data = {"status": "SOME STATUS HERE"}
        return Response(response_data, status=status.HTTP_200_OK)


class View:
    def __init__(self):
        self.gateway = OfflineGateway


view = View()
