from shop.actions.base import BaseACTION
import json
from datetime import datetime
import os
from shop.custom_s3_storage import MediaStorage
from django.http.response import HttpResponse, JsonResponse
from shop.configs import *
from shop.enums import *
from shop.models import *
from contactus.models import *


class RequestCallbackACTION(BaseACTION):
    action = StateAction.REQUEST_CALLBACK.value

    def execute(self):
        request = self.request
        try:
            user = request.user
            next_states = ORDER_STATE_WORKFLOW.get(self.action, {}).get(
                "next_states", []
            )
            if self.order:
                self.order.append_states(next_states)
            else:
                CallbackRequest.objects.create(name=user.name, phone=user.phone_number)
            return next_states
        except Exception as e:
            raise ValueError(e)
