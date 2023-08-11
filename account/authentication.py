from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from account.models import TenantUser

ProfileUser = get_user_model()
# TenantUser = get_user_model("account.models.TenantUser")


class ProfileUserAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        user = authentication.get_authorization_header(request).split()

        if not user:
            return None

        try:
            user = ProfileUser.objects.get(username=user[0])

        except ProfileUser.DoesNotExist:
            return AuthenticationFailed("Invalid username.")

        return (user, None)


class TenantUserAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        user = authentication.get_authorization_header(request).split()

        if not user:
            return None

        try:
            user = TenantUser.objects.get(username=user[0])

        except TenantUser.DoesNotExist:
            return AuthenticationFailed("Invalid username.")

        return (user, None)
