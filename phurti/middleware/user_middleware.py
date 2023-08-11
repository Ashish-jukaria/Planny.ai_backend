from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.models import TenantUser, Profile
from django.conf import settings
from rest_framework import status


class SetAuthUserModelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and "Bearer " in auth_header:
            token = auth_header.split(" ")[1]
            try:
                decoded_token = JWTAuthentication().get_validated_token(token)
                user_type = decoded_token.payload.get("user_type")

                if user_type == "tenant":
                    request.user = TenantUser()
                    settings.AUTH_USER_MODEL = "account.TenantUser"
                elif user_type == "profile":
                    request.user = Profile()
                    settings.AUTH_USER_MODEL = "account.Profile"
                else:
                    return JsonResponse(
                        {"error": "Invalid user type in token."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Exception as error:
                return JsonResponse(
                    {"error": "Invalid authentication token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        response = self.get_response(request)

        return response
