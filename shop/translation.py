from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from shop.models import BillingType, Product, Category


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "amount",
        "short_description",
        "description",
        "image"
    )


@register(BillingType)
class BillingTypeTranslationOptions(TranslationOptions):
    fields = (
        "display_name",
    )
