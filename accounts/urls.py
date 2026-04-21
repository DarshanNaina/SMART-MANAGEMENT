from django.urls import path

from .views import (
    home,
    login_view,
    redirect_dashboard,
    register_view,
    resend_login_otp_view,
    resend_registration_otp_view,
    secret_key_verification_view,
    user_logout_view,
    verify_login_otp_view,
    verify_registration_otp_view,
)

app_name = "accounts"

urlpatterns = [
    path("", home, name="home"),
    path("register/", register_view, name="register"),
    path("register/teacher/", lambda request: register_view(request, role="TEACHER"), name="register_teacher"),
    path("register/admin/", lambda request: register_view(request, role="ADMIN"), name="register_admin"),
    path("secret-key-verification/", secret_key_verification_view, name="secret_key_verification"),
    path("verify-registration-otp/", verify_registration_otp_view, name="verify_registration_otp"),
    path("resend-registration-otp/", resend_registration_otp_view, name="resend_registration_otp"),
    path("login/", login_view, name="login"),
    path("verify-login-otp/", verify_login_otp_view, name="verify_login_otp"),
    path("resend-login-otp/", resend_login_otp_view, name="resend_login_otp"),
    path("logout/", user_logout_view, name="logout"),
    path("redirect-dashboard/", redirect_dashboard, name="redirect_dashboard"),
]
