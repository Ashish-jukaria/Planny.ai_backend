from rest_framework.permissions import BasePermission
from account.models import TenantUser, Profile


class IsTenantUser(BasePermission):
    def has_permission(self, request, view):
        print("sdfjbsdfjs")
        print(self)
        return bool(
            request.user.is_authenticated
            and TenantUser.objects.filter(pk=request.user.id).exists()
        )


class IsProfileUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and Profile.objects.filter(pk=request.user.id).exists()
        )
