import re

from django.db import models
from django.utils.translation import gettext_lazy as _


class GoogleFontSubset(models.Model):
    name = models.CharField(_("Name"), max_length=125)

    def __str__(self):
        return self.name


class GoogleFontVariant(models.Model):
    weight = models.PositiveIntegerField(_("Font Weight"))
    style = models.CharField(_("Font Style"), max_length=125)
    variant_id = models.CharField(_("Variant ID"), unique=True, max_length=125)

    def save(self, *args, **kwargs):
        weight = re.findall(r"\d+", self.variant_id)
        self.weight = (
            weight[0] if weight else 400
        )  # Because Fonts API returns 400 fonts as "regular" and "italic" but other variants are "100" or "100italic"
        style = re.sub(r"\d+", "", self.variant_id)
        self.style = (
                style or "regular"
        )  # Regular fonts are returned just as 400, 500, ...

        super(GoogleFontVariant, self).save()

    def __str__(self):
        return self.variant_id


class GoogleFont(models.Model):
    family = models.CharField(_("Font Family"), max_length=125)
    version = models.CharField(_("Font Version"), default="v1", max_length=16)
    category = models.CharField(_("Font Category"), max_length=125)
    variants = models.ManyToManyField(
        GoogleFontVariant,
        verbose_name=_("Font Variants"),
    )
    subsets = models.ManyToManyField(
        GoogleFontSubset,
        verbose_name=_("Font Subsets"),
    )

    class Meta:
        ordering = ("family",)

    def url(self):
        variants = self.variants.values_list("variant_id", flat=True)
        return f"https://fonts.googleapis.com/css?family={self.family}:{','.join(variants)}"

    def get_by_natural_key(self, sigla):
        return self.get(sigla=sigla)

    def __str__(self):
        return self.family


def get_default_font():
    return GoogleFont.objects.get_or_create(family="Space Grotesk", defaults={"category": "sans-serif"})[0]


def get_default_font_id():
    return get_default_font().id
