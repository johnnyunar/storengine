import base64
from xml.dom.minidom import parseString

import requests
import xmltodict
from dicttoxml import dicttoxml
from django.conf import settings

from shop import models


class Packeta:
    """
    Class for Packeta API requests
    """

    BASE_URL = settings.PACKETA_BASE_URL
    API_PASSWORD = settings.PACKETA_API_PASSWORD

    def __generate_packet_xml(
        self,
        order_number,
        first_name,
        last_name,
        email,
        packeta_point_id,
        price,
        cod_amount,
    ):
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
                <eshop>RISTRE</eshop>
            </packetAttributes>
        </createPacket>
        """.format(
            api_password=self.API_PASSWORD,
            order_number=order_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            packeta_point_id=packeta_point_id,
            price=price,
            cod_amount=cod_amount,
        )

    def __xml_id_func(self, parent):
        return "id"

    def __generate_packet_labels_xml(self, packet_ids):
        orders = []
        for number in packet_ids:
            orders.append(number)

        data = {
            "packetsLabelsPdf": {
                "apiPassword": self.API_PASSWORD,
                "packetIds": orders,
                "format": "A7 on A4",
                "offset": 0,
            }
        }
        xml = dicttoxml(data, attr_type=False, root=False, item_func=self.__xml_id_func)
        return parseString(xml).toprettyxml().split("\n", 1)[-1]

    def create_packet(
        self,
        order_number,
        first_name,
        last_name,
        email,
        packeta_point_id,
        price,
        cod_amount,
    ):
        response = requests.post(
            self.BASE_URL,
            headers={"Content-Type": "application/xml"},
            data=self.__generate_packet_xml(
                order_number,
                first_name,
                last_name,
                email,
                packeta_point_id,
                price,
                cod_amount,
            ).encode("utf-8"),
        )

        print(response.text)
        tree = xmltodict.parse(response.text)
        packet_id = tree["response"]["result"]["id"]
        packet_barcode = tree["response"]["result"]["barcode"]
        packet_barcode_text = tree["response"]["result"]["barcodeText"]
        new_packet = models.Packet(
            packet_id=packet_id,
            packet_barcode=packet_barcode,
            packet_barcode_text=packet_barcode_text,
        )
        new_packet.save()

        order = models.Order.objects.get(order_number=order_number)
        order.packet = new_packet
        order.save()

        return response.text

    def get_packet_labels_pdf(self, packet_ids):
        response = requests.post(
            self.BASE_URL,
            headers={"Content-Type": "application/xml"},
            data=self.__generate_packet_labels_xml(packet_ids),
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
            api_password=self.API_PASSWORD, packet_id=packet_id
        )
        response = requests.post(
            self.BASE_URL, headers={"Content-Type": "application/xml"}, data=data
        )
        if response.status_code == 200:
            tree = xmltodict.parse(response.text)
            if tree.get("response").get("status") == "ok":
                status_code = int(tree.get("response").get("result").get("statusCode"))
                status_name = tree.get("response").get("result").get("codeText")
                status_display_name = (
                    tree.get("response").get("result").get("statusText")
                )

                return status_code, status_name, status_display_name

        return None, None, None
