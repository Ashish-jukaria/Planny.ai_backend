from shop.actions.base import BaseACTION
import json
from datetime import datetime
import os
from shop.custom_s3_storage import MediaStorage
from django.http.response import HttpResponse, JsonResponse
from shop.configs import *
from shop.enums import *
from shop.models import *


class UploadPrescriptionACTION(BaseACTION):
    action = StateAction.UPLOAD_PRESCRIPTION.value

    def execute(self):
        state = self.state
        request = self.request
        user = request.user
        try:
            self.order = Order.objects.initialize(user)
            file_obj = state["media"]
            file_directory_within_bucket = "{userid}".format(userid=user.id)
            file_path_within_bucket = os.path.join(
                file_directory_within_bucket, file_obj.name
            )
            media_storage = MediaStorage()
            media_storage.save(file_path_within_bucket, file_obj)
            file_url = media_storage.url(file_path_within_bucket)
            self.order.prescription_url = file_url
            next_states = ORDER_STATE_WORKFLOW.get(self.action, {}).get(
                "next_states", []
            )
            for next_state in next_states:
                if next_state["state_type"] == StateType.SHOW_MEDIA.value:
                    next_state["body"]["value"] = file_url
            self.order.append_states(next_states)
            self.order.save()
            return next_states
        except Exception as e:
            raise ValueError(e)
