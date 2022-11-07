import base64
import logging
from xml.dom.minidom import parseString

import requests
import xmltodict
from dicttoxml import dicttoxml
from django.conf import settings
from wagtail.models import Site

from shop import models

logger = logging.getLogger("django")


class Packeta:
    """
    Class for Packeta API requests
    """

    def __init__(self):
        self.base_url = settings.PACKETA_BASE_URL
        self.api_password = settings.PACKETA_API_PASSWORD

    def _generate_packet_xml(
            self,
            order_number,
            first_name,
            last_name,
            email,
            packeta_point_id,
            price,
            currency,
            cod_amount,
            weight_kg,
    ):
        from core.models import ContactSettings

        return """
        <createPacket>
            <apiPassword>{api_password}</apiPassword>
            <packetAttributes>
                <number>{order_number}</number>
                <name>{first_name}</name>
                <surname>{last_name}</surname>
                <email>{email}</email>
                <addressId>{packeta_point_id}</addressId>
                <cod>{cod_amount}</cod>
                <value>{price}</value>
                <currency>{currency}</currency>
                <weight>{weight_kg}</weight>
                <eshop>{sender_id}</eshop>
            </packetAttributes>
        </createPacket>
        """.format(
            api_password=self.api_password,
            order_number=order_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            packeta_point_id=packeta_point_id,
            price=price,
            currency=currency,
            cod_amount=cod_amount,
            weight_kg=weight_kg,
            sender_id=settings.PACKETA_SENDER_ID,
        )

    def _xml_id_func(self, parent):
        return "id"

    def _generate_packet_labels_xml(self, packet_ids):
        orders = []
        for number in packet_ids:
            orders.append(number)

        data = {
            "packetsLabelsPdf": {
                "apiPassword": self.api_password,
                "packetIds": orders,
                "format": "A7 on A4",
                "offset": 0,
            }
        }
        xml = dicttoxml(
            data, attr_type=False, root=False, item_func=self._xml_id_func
        )
        return parseString(xml).toprettyxml().split("\n", 1)[-1]

    def create_packet(
            self,
            order_number,
            first_name,
            last_name,
            email,
            packeta_point_id,
            price,
            currency,
            cod_amount,
            weight_kg,
    ):
        response = requests.post(
            self.base_url,
            headers={"Content-Type": "application/xml"},
            data=self._generate_packet_xml(
                order_number,
                first_name,
                last_name,
                email,
                packeta_point_id,
                price,
                currency,
                cod_amount,
                weight_kg,
            ).encode("utf-8"),
        )

        logger.info(response.text)

        try:
            tree = xmltodict.parse(response.text)
            packet_id = tree["response"]["result"]["id"]
            packet_barcode = tree["response"]["result"]["barcode"]
            packet_barcode_text = tree["response"]["result"]["barcodeText"]
            new_packet = models.Packet(
                packet_id=packet_id,
                barcode=packet_barcode,
                barcode_text=packet_barcode_text,
            )
            new_packet.save()

            order = models.Order.objects.get(order_number=order_number)
            order.packet = new_packet
            order.save()
        except KeyError:
            logger.info("Unable to create a Packet.")

        return response.text

    def create_packet_from_order(self, order):
        return self.create_packet(
            order.order_number,
            order.shipping_address.first_name,
            order.shipping_address.last_name,
            order.shipping_address.email,
            order.packeta_point_id,
            order.total_price.amount,
            order.total_price.currency,
            order.total_price.amount if not order.is_paid else 0,
            order.total_weight_kg,
        )

    def get_packet_labels_pdf(self, packet_ids):
        response = requests.post(
            self.base_url,
            headers={"Content-Type": "application/xml"},
            data=self._generate_packet_labels_xml(packet_ids),
        )
        tree = xmltodict.parse(response.text)
        encoded_file = tree["response"]["result"]
        decoded_file = base64.b64decode(encoded_file)
        return decoded_file

    def get_packet_status(self, packet_id):
        data = """
        <packetStatus>
            <apiPassword>{api_password}</apiPassword>
            <packetId>{packet_id}</packetId>
        </packetStatus>
        """.format(
            api_password=self.api_password, packet_id=packet_id
        )
        response = requests.post(
            self.base_url,
            headers={"Content-Type": "application/xml"},
            data=data,
        )
        if response.status_code == 200:
            tree = xmltodict.parse(response.text)
            if tree.get("response").get("status") == "ok":
                status_code = int(
                    tree.get("response").get("result").get("statusCode")
                )
                status_name = (
                    tree.get("response").get("result").get("codeText")
                )
                status_display_name = (
                    tree.get("response").get("result").get("statusText")
                )

                return status_code, status_name, status_display_name

        return None, None, None
