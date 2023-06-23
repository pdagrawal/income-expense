from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (
    EmailValidationView,
    LoginView,
    PasswordReset,
    RegistrationView,
    RequestPasswordResetEmail,
    UsernameValidationView,
    VerificationView,
)

urlpatterns = [
    path("register", RegistrationView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "validate-username",
        csrf_exempt(UsernameValidationView.as_view()),
        name="validate-username",
    ),
    path(
        "validate-email",
        csrf_exempt(EmailValidationView.as_view()),
        name="validate-email",
    ),
    path("activate/<uidb64>/<token>", VerificationView.as_view(), name="activate"),
    path(
        "request-reset-link",
        RequestPasswordResetEmail.as_view(),
        name="request-password",
    ),
    path(
        "reset-pasword/<uidb64>/<token>", PasswordReset.as_view(), name="reset-pasword"
    ),
]
