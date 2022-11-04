from django.db import models
from django.utils.translation import gettext_lazy as _

from shop.api.packeta_api import Packeta


class Packet(models.Model):
    packet_id = models.CharField(_("Packet ID"), max_length=25)
    barcode = models.CharField(_("Barcode"), max_length=25)
    barcode_text = models.CharField(
        _("Barcode Text"),
        max_length=25,
    )

    status_code = models.IntegerField(_("Status Code"), null=True, blank=True)
    status_name = models.CharField(
        _("Status Name"),
        max_length=255,
        blank=True,
        null=True,
        default="",
    )
    status_display_name = models.CharField(
        _("Status Display Name"),
        max_length=255,
        blank=True,
        null=True,
        default="",
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return self.packet_id

    def get_status(self):
        packeta = Packeta()
        return packeta.get_packet_status(self.packet_id)

    class Meta:
        verbose_name = _("Packet")
        verbose_name_plural = _("Packets")
