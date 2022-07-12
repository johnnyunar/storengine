from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View

from users.models import CookiesPreferences


class SetCookiesPreferencesView(View):
    """
    View that accepts a post request with cookies data. The consents are later saved in session
    and in case a user is logged-in, they are also saved in database and connected to the user.
    """

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        important_cookies = request.POST.get("important", False) == "on"
        analytic_cookies = request.POST.get("analytic", False) == "on"
        marketing_cookies = request.POST.get("marketing", False) == "on"

        request.session["important_cookies"] = important_cookies
        request.session["analytic_cookies"] = analytic_cookies
        request.session["marketing_cookies"] = marketing_cookies
        request.session["cookies_preferences_set"] = True

        if user:
            cookies = CookiesPreferences.objects.create(
                important_cookies_accepted=timezone.now() if important_cookies else None,
                analytic_cookies_accepted=timezone.now() if analytic_cookies else None,
                marketing_cookies_accepted=timezone.now() if marketing_cookies else None,
            )
            user.cookies_preferences = cookies
            user.save()

        return JsonResponse({"success": True}, headers={"HX-Refresh": "true"})

    def get(self, request):
        return HttpResponseRedirect(reverse_lazy("home"))
