from modeltranslation.translator import register, TranslationOptions

from core.models import SiteConfiguration, Button, FrequentlyAskedQuestion, Counter


@register(SiteConfiguration)
class SiteConfigurationTranslationOptions(TranslationOptions):
    fields = (
        "notification_bar_text",
        "subheading_text",
        "about_me_text",
        "quiz_heading",
        "quiz_subheading",
        "ebook_text",
        "gdpr_text",
        "gdpr_file",
        "terms_and_conditions_text",
        "terms_and_conditions_file",
    )


@register(Button)
class ButtonTranslationOptions(TranslationOptions):
    fields = (
        "text",
        "link",
        "custom_html"
    )


@register(Counter)
class CounterTranslationOptions(TranslationOptions):
    fields = ("text",)


@register(FrequentlyAskedQuestion)
class FAQTranslationOptions(TranslationOptions):
    fields = (
        "question",
        "answer",
    )
