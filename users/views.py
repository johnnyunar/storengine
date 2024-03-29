import logging

from django.contrib.auth import login, user_logged_in
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import MultipleObjectsReturned
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, DeleteView, TemplateView

from shop.models import Order, Cart
from users.forms import ShopUserCreationForm
from users.models import ShopUser

logger = logging.getLogger("django")


def set_session_cookies_preferences(request, user):
    if user.cookies_preferences:
        request.session["important_cookies"] = bool(
            user.cookies_preferences.important_cookies_accepted
        )
        request.session["analytic_cookies"] = bool(
            user.cookies_preferences.analytic_cookies_accepted
        )
        request.session["marketing_cookies"] = bool(
            user.cookies_preferences.marketing_cookies_accepted
        )
        request.session["cookies_preferences_set"] = True

        logger.info(
            f"Cookies Preferences for session updated. {request.session}"
        )


def set_session_cart(request, user):
    try:
        cart = Cart.objects.get(created_by=user)
        request.session["cart"] = cart.pk
        logger.info(f"Cart set for session. {request.session}")
    except MultipleObjectsReturned:
        Cart.objects.filter(created_by=user).delete()
        logger.info(
            f"Too many carts for user - deleted all cart instances. "
            f"{request.session}"
        )
    except Cart.DoesNotExist:
        pass


@receiver(user_logged_in)
def set_user_session(sender, user, request, **kwargs):
    set_session_cookies_preferences(request, user)
    set_session_cart(request, user)


class CustomLoginView(LoginView):
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        super(CustomLoginView, self).form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class SignupView(FormView):
    template_name = "registration/signup.html"
    form_class = ShopUserCreationForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        new_user = form.save()
        login(self.request, new_user)
        return super().form_valid(form)


class AccountView(LoginRequiredMixin, UpdateView):
    template_name = "users/account_index.html"
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("profile")
    model = ShopUser
    fields = ("avatar", "first_name", "last_name", "email")

    def get_object(self, queryset=None):
        return self.request.user


class AccountOrdersView(LoginRequiredMixin, TemplateView):
    template_name = "users/account_orders.html"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super(AccountOrdersView, self).get_context_data()
        context["orders"] = Order.objects.filter(created_by=self.request.user)
        return context


class CustomUserDeleteView(LoginRequiredMixin, DeleteView):
    model = ShopUser
    success_url = reverse_lazy("home")
    template_name = "users/account_delete_confirm.html"

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        """
        Keep the object and its PK, everything else is removed. Then redirect to the
        success URL.
        """

        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.email = "[deleted]"
        self.object.first_name = "[deleted]"
        self.object.last_name = "[deleted]"
        self.object.avatar.delete()
        self.object.avatar = "accounts/default-user.png"
        self.object.set_password(
            ShopUser.objects.make_random_password(length=32)
        )
        self.object.save()

        return HttpResponseRedirect(success_url)


class CustomUserDeactivateView(LoginRequiredMixin, DeleteView):
    model = ShopUser
    success_url = reverse_lazy("home")
    template_name = "users/account_deactivate_confirm.html"

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        """
        Keep the object and its PK, everything else is removed. Then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()

        return HttpResponseRedirect(success_url)
