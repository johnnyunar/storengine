import os
import re

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

from core.models import GoogleFont
from core.models.fonts import GoogleFontVariant, GoogleFontSubset


def update_google_fonts():
    """Generate GoogleFont objects based on Google Font API"""
    url = "https://www.googleapis.com/webfonts/v1/webfonts"
    params = {"key": settings.GOOGLE_API_KEY}
    fonts = requests.get(url, params=params).json()["items"]

    for font in fonts:
        google_font, _font_created = GoogleFont.objects.update_or_create(
            family=font["family"],
            defaults={"version": font["version"], "category": font["category"]},
        )
        for variant_id in font["variants"]:
            font_variant, _variant_created = GoogleFontVariant.objects.get_or_create(variant_id=variant_id)
            google_font.variants.add(font_variant)
        for subset_name in font["subsets"]:
            font_subset, _subset_created = GoogleFontSubset.objects.get_or_create(name=subset_name)
            google_font.subsets.add(font_subset)


def start():
    """
    The Google Font updater calls the update_google_fonts function every 24 hours to keep the local fonts up-to-date.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_google_fonts(), "interval", hours=24)
    scheduler.start()
