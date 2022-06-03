from django.contrib.auth import views as auth_views
from django.urls import path

from users.views import (
    SignupView,
    AccountView,
    CustomUserDeactivateView,
    CustomUserDeleteView,
    AccountOrdersView,
    CustomLoginView,
)

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("profile/", AccountView.as_view(), name="profile"),
    path("profile/orders/", AccountOrdersView.as_view(), name="account_orders"),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            html_email_template_name="registration/password_reset_html_email.html"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "deactivate-account/",
        CustomUserDeactivateView.as_view(),
        name="deactivate_account",
    ),
    path(
        "delete-account/",
        CustomUserDeleteView.as_view(),
        name="delete_account",
    ),
]
