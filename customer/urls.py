from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import *

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("sendotp/<str:phone>/", sendOTP, name="sendOTP"),
    path(
        "verifyotp/<str:phone>/<str:session_id>/<str:otp>/", verifyOTP, name="verifyOTP"
    ),
    # path('add_alternative/', AlternativeUpdate, name="AlternativeUpdate")
]
