from django.core.exceptions import PermissionDenied


def inventory_lock_check(function):
    def wrap(request, *args, **kwargs):
        if not request.user.inventory.is_active:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
