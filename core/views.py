from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, CreateView

from core.models import Testimonial, FrequentlyAskedQuestion, Counter, QuizRecord
from shop.models import Product
from users.models import CookiesPreferences


class HomePageView(TemplateView):
    template_name = "storengine/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data()
        context["testimonials"] = Testimonial.objects.all()
        context["services"] = Product.objects.filter(is_active=True)[:3]
        context["counters"] = Counter.objects.filter(is_active=True)
        return context


class ContactView(TemplateView):
    template_name = "storengine/contact.html"


class FAQView(TemplateView):
    template_name = "storengine/faq.html"

    def get_context_data(self, **kwargs):
        context = super(FAQView, self).get_context_data()
        context["faqs"] = FrequentlyAskedQuestion.objects.filter(is_active=True)
        return context


class QuizView(CreateView):
    template_name = "storengine/quiz.html"
    model = QuizRecord
    success_url = "/"

    fields = "__all__"


class GDPRView(TemplateView):
    template_name = "storengine/gdpr.html"


class TermsAndConditionsView(TemplateView):
    template_name = "storengine/terms_and_conditions.html"


class SetCookiesPreferencesView(View):
    def post(self, request, *args, **kwargs):
        print(request.POST)
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
