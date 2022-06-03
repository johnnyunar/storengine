from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import ShopUser


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = ShopUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = ShopUser
        fields = ("email",)
