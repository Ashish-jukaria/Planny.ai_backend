from shop.configs import *
from shop.enums import *


class BaseACTION:
    action = StateAction.NO_ACTION.value

    def __init__(self, request=None, state=None, order=None, **kwargs):
        if state is None:
            state = {}
        self.request = request
        self.order = order
        self.state = state

    def execute(self):
        return ORDER_STATE_WORKFLOW.get(self.action, {}).get("next_state", {})
