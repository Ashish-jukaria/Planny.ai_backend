from datetime import datetime
from shop.enums import *

STATE_DATE_FORMAT = "%B %Y, %H:%M%p"

DEFAULT_ORDER_STATE = {
    "state_list": [
        {
            "action": None,
            "state_type": StateType.TEXT.value,
            "sender": Sender.AIKAM.value,
            "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
            "body": {
                "value": "Welcome to Aikam\nNow get your medicines at your doorstep with huge discount",
                "media_width": None,
                "media_height": None,
                "thumbnail_image": {"url": None, "height": None, "width": None},
            },
        },
        {
            "action": StateAction.REQUEST_CALLBACK.value,
            "state_type": StateType.REQUEST_CALLBACK.value,
            "sender": Sender.AIKAM.value,
            "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
            "body": {
                "value": None,
                "media_width": None,
                "media_height": None,
                "thumbnail_image": {"url": None, "height": None, "width": None},
            },
        },
        {
            "action": StateAction.UPLOAD_PRESCRIPTION.value,
            "state_type": StateType.UPLOAD_PRESCRIPTION.value,
            "sender": Sender.AIKAM.value,
            "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
            "body": {
                "value": None,
                "media_width": None,
                "media_height": None,
                "thumbnail_image": {"url": None, "height": None, "width": None},
            },
        },
    ],
}


ORDER_STATE_WORKFLOW = {
    StateAction.NO_ACTION.value: {
        "next_states": [
            {
                "action": None,
                "state_type": str(StateType.TEXT.value),
                "sender": Sender.AIKAM.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": "Thank you for reaching out to us. Someone from our team will call you",
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            }
        ],
        "next_status": None,
    },
    StateAction.REPLY.value: {
        "next_states": [
            {
                "action": None,
                "state_type": str(StateType.TEXT.value),
                "sender": Sender.AIKAM.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": "Thank you for reaching out to us. Someone from our team will call you",
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            }
        ],
        "next_status": None,
    },
    StateAction.UPLOAD_PRESCRIPTION.value: {
        "next_states": [
            {
                "action": StateType.SHOW_MEDIA.value,
                "state_type": StateType.SHOW_MEDIA.value,
                "sender": Sender.CLIENT.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": None,
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            },
            {
                "action": None,
                "state_type": StateType.TEXT.value,
                "sender": Sender.AIKAM.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": "Thank you for uploading prescription, we will get back to you once item list is verified",
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            },
            {
                "action": StateAction.RE_UPLOAD_PRESCRIPTION.value,
                "state_type": StateType.RE_UPLOAD_PRESCRIPTION.value,
                "sender": Sender.AIKAM.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": None,
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            },
        ],
        "next_status": Status.INITIALISED.value,
    },
    StateAction.RE_UPLOAD_PRESCRIPTION.value: {
        "next_states": [
            {
                "action": StateType.SHOW_MEDIA.value,
                "state_type": StateType.SHOW_MEDIA.value,
                "sender": Sender.CLIENT.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": None,
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            },
            {
                "action": None,
                "state_type": StateType.TEXT.value,
                "sender": Sender.AIKAM.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": "Thank you for re uploading prescription, we will get back to you once item list is verified",
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            },
            {
                "action": StateAction.RE_UPLOAD_PRESCRIPTION.value,
                "state_type": StateType.RE_UPLOAD_PRESCRIPTION.value,
                "sender": Sender.AIKAM.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": None,
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            },
        ],
        "next_status": None,
    },
    StateAction.REQUEST_CALLBACK.value: {
        "next_states": [
            {
                "action": None,
                "state_type": str(StateType.TEXT.value),
                "sender": Sender.AIKAM.value,
                "created_on": datetime.now().strftime(STATE_DATE_FORMAT),
                "body": {
                    "value": "Thank you for reaching out to us. Someone from our team will call you",
                    "media_width": None,
                    "media_height": None,
                    "thumbnail_image": {"url": None, "height": None, "width": None},
                },
            }
        ],
        "next_status": None,
    },
}
