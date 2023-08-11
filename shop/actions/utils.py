from shop import actions


def get_action_class(action):
    if action:
        init, *temp = action.split("_")
        action_name = "".join([init.lower().capitalize(), *map(str.title, temp)])
        action_class_name = "%sACTION" % action_name
        action_class = getattr(actions, action_class_name, actions.BaseACTION)
        return action_class
    else:
        return actions.BaseACTION()
