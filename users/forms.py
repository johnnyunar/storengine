from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import ShopUser


class ShopUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = ShopUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class ShopUserChangeForm(UserChangeForm):
    class Meta:
        model = ShopUser
        fields = ("email",)


class ShopUserWagtailCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = ShopUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "avatar",
        )


class ShopUserWagtailChangeForm(UserChangeForm):
    class Meta:
        model = ShopUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "avatar",
        )
