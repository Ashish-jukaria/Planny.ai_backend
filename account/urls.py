from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework import routers
from .views import *

router = routers.SimpleRouter()
router.register(r"profile", ProfileViewSet)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),  # Login View
    path(
        "login/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),  # Refresh Token View
    path("register/", RegistrationView.as_view(), name="register"),  # Registration View
    path("sendotp/<str:phone>/", sendOTP, name="sendOTP"),  # Send OTP View
    path(
        "verifyotp/<str:phone>/<str:session_id>/<str:otp>/", verifyOTP, name="verifyOTP"
    ),  # Verify OTP View
    path(
        "add_alternative/", AlternativeUpdate.as_view(), name="AlternativeUpdate"
    ),  # Add user alternatives
    path("feedback/", feedback, name="feedback"),  # Add user feedback
    path(
        "userprofile/", UserProfileView.as_view(), name="userProfile"
    ),  # User Profile View
    path("wallet/", WalletView.as_view(), name="wallet"),  # User Wallet View
    path("tenants/", TenantView.as_view(), name="tenantPost"),  # Tenant POST
    path(
        "tenants/<int:id>", TenantView.as_view(), name="tenantView"
    ),  # Tenant GET,PUT,DELET
    path(
        "tenant_user/register/", TenanteUserRegisterView.as_view(), name="auth_register"
    ),
    path(
        "tenant_user/tenant_user_send_otp/",
        tenant_user_send_otp,
        name="tenant_user_send_otp",
    ),  # Send OTP View
    path(
        "tenant_user/verifyotp/", tenant_user_verify_otp, name="tenant_user_verify_otp"
    ),  # Verify OTP View
    path(
        "subscriptions/", SubscriptionView.as_view(), name="subscription"
    ),  # User Subscription View
    path(
        "detail_subscriptions/",
        SubscriptionDetailView.as_view(),
        name="detail_subscription",
    ),  # Detail User Subscription View
    path("tenant_categories/", TenantCategoryList.as_view(), name="tenant_categories"),
    # payment urls for subscription bought by tenant user
    path(
        "payment/initiate/",
        PaymentViewSet.as_view({"post": "initiate"}),
        name="payment-initiate",
    ),
    path(
        "payment/success/",
        PaymentViewSet.as_view({"post": "success"}),
        name="payment-success",
    ),
    path(
        "payment/failure/",
        PaymentViewSet.as_view({"post": "failure"}),
        name="payment-failure",
    ),
    path("user/tenants/", UserAllTenantView.as_view(), name="user_all_tenants"),

    path('tenants/search/', TenantSearchAPI.as_view(), name='tenant_search'),

]

urlpatterns += router.urls
