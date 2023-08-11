from rest_framework_simplejwt.authentication import JWTAuthentication
from account.models import Profile, TenantUser


def set_user(view_function):
    def decorated_function(request, *args, **kwargs):
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            token = auth_header.split(" ")[1]
            decoded_token = JWTAuthentication().get_validated_token(token)
            user_type = decoded_token.payload["user_type"]
            phone_number = decoded_token.payload["phone_number"]
            user_id = decoded_token.payload["user_id"]

            if user_type == "tenant":
                user = TenantUser.objects.get(id=user_id, phone_number=phone_number)
                request.user = user
            elif user_type == "profile":
                user = Profile.objects.get(id=user_id, phone_number=phone_number)
                request.user = user
        else:
            request.user = None

        return view_function(request, *args, **kwargs)

    return decorated_function
