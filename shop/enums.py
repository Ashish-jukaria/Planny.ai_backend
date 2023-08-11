from enum import Enum
from datetime import datetime


class StateType(Enum):
    TEXT = "TEXT"
    REQUEST_CALLBACK = "REQUEST_CALLBACK"
    UPLOAD_PRESCRIPTION = "UPLOAD_PRESCRIPTION"
    RE_UPLOAD_PRESCRIPTION = "RE_UPLOAD_PRESCRIPTION"
    SHOW_MEDIA = "SHOW_MEDIA"


class StateAction(Enum):
    NO_ACTION = "NO_ACTION"
    REPLY = "REPLY"
    REQUEST_CALLBACK = "REQUEST_CALLBACK"
    UPLOAD_PRESCRIPTION = "UPLOAD_PRESCRIPTION"
    RE_UPLOAD_PRESCRIPTION = "RE_UPLOAD_PRESCRIPTION"
    SHOW_MEDIA = "SHOW_MEDIA"


class Status(Enum):
    INITIALISED = "INITIALISED"
    CANCELLED = "CANCELLED"
    DELIVERED = "DELIVERED"
    IN_TRANSIT = "IN_TRANSIT"
    INVOICE_GENERATED = "INVOICE_GENERATED"
    ORDER_PLACED = "ORDER_PLACED"
    REFUND_INITIATED = "REFUND_INITIATED"
    REFUNDED_AND_CLOSED = "REFUNDED_AND_CLOSED"
    DISCARDED = "DISCARDED"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class FulfilmentType(Enum):
    TAKE_AWAY = "TAKE_AWAY"
    DELIVERY = "DELIVERY"


class Sender(Enum):
    AIKAM = "AIKAM"
    CLIENT = "CLIENT"
