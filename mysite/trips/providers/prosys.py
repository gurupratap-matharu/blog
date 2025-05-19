import logging
import random
from datetime import datetime

from django.conf import settings
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from django.utils import timezone

import requests
from lxml import etree
from zeep import Client
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin
from zeep.transports import Transport

logger = logging.getLogger(__name__)

transport = Transport(cache=SqliteCache(), timeout=10)

STOPS_MAP = {
    "GYU": {
        "IdParada": 393,
        "Descripcion": "Gualeguaychú",
        "Localidad": ".",
        "Partido": "GUALEGUAYCHU",
        "Provincia": "ENTRE RÍOS",
        "Pais": "Argentina",
    },
    "BUE": {
        "IdParada": 449,
        "Descripcion": "RETIRO",
        "Localidad": "Ciudad Autonoma de Buenos Aires",
        "Partido": "Ciudad Autonoma de Bs. As.",
        "Provincia": "Buenos Aires",
        "Pais": "Argentina",
    },
}


class Prosys:
    url = settings.CATA_WSDL
    user = settings.CATA_USER
    password = settings.CATA_PASSWORD
    web_id = settings.CATA_WEB_ID
    web_agency_id = settings.CATA_WEB_AGENCY_ID
    key = settings.CATA_KEY

    history = HistoryPlugin()

    def __init__(self, connection_id=None):
        try:
            self.client = Client(self.url, transport=transport, plugins=[self.history])

        except requests.exceptions.ConnectionError as e:
            logger.warn("Prosys ConnectionError:%s" % e)
            mail_admins("Prosys ConnectionError", f"Connection Id:{connection_id}")
            return

        except requests.exceptions.Timeout as e:
            logger.warn("Prosys Timeout:%s" % e)
            mail_admins("Prosys Timeout", f"Connection Id:{connection_id}")
            return

        except requests.exceptions.HTTPError as e:
            logger.warn("Prosys HTTPError:%s" % e)
            mail_admins("Prosys HTTPError", f"Connection Id:{connection_id}")
            return

        except requests.exceptions.RequestException as e:
            logger.warn("Prosys Error:%s" % e)
            mail_admins("Prosys Error", f"Connection Id:{connection_id}")
            return

        if connection_id:
            self.connection_id = connection_id
            logger.info("using existing connection:%s" % connection_id)
        else:
            self.connection_id = self.start_session()
            logger.info("created new connection:%s" % self.connection_id)

    def start_session(self):
        response = self.client.service.StartSession(
            self.web_id, self.user, self.password, self.key
        )
        connection_id = response.xpath("//ConnectionId")[0].text
        is_ok = response.xpath("//IsOk")[0].text
        has_warnings = response.xpath("//HasWarnings")[0].text

        logger.info("connecton_id:%s" % connection_id)
        logger.info("is_ok?:%s" % is_ok)
        logger.info("has_warnings?:%s" % has_warnings)

        return connection_id

    def search(self, origin, destination, departure):
        origin, destination = STOPS_MAP.get(origin, {}), STOPS_MAP.get(destination, {})

        # added dummy id's below for which we don't have any map. Remove them later
        origin_id = origin.get("IdParada", 123)
        destination_id = destination.get("IdParada", 456)

        logger.info(
            "searching from:%s to:%s on:%s" % (origin_id, destination_id, departure)
        )

        response = self.client.service.GetByFechaOrigenDestino(
            self.web_id,
            self.web_agency_id,
            origin_id,
            destination_id,
            departure,
            self.user,
            self.password,
            self.connection_id,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())
        keys = response.findall("Servicio")
        trips = [self._parse_service(key) for key in keys]
        data = dict()
        data["origin"] = origin.get("Descripcion", "").title()
        data["destination"] = destination.get("Descripcion", "").title()
        data["departure"] = response.get("Fecha", "")
        data["trips"] = trips

        return data

    def get_route(self, service_id):
        """
        Provides information about all stops for a trip with arrival and departure times.
        """

        response = self.client.service.GetRecorridoByID2(
            self.web_id,
            service_id,
            self.connection_id,
            self.user,
            self.password,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        stops = response.findall("Parada")
        route = [self._parse_stop(key) for key in stops]

        logger.info("Route:%s" % route)

        return route

    def get_service_features(self, service_id):
        """
        Description of amenities for a trip.
        This method doesn't work and is incomplete.
        """

        response = self.client.service.GetServiceFeatures(
            self.web_id,
            self.user,
            self.password,
            service_id,
            self.connection_id,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        return response

    def get_service(self, service_id):
        data = dict()

        response = self.client.service.GetServiceData(
            self.web_id,
            self.user,
            self.password,
            service_id,
            self.connection_id,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        el_stops = response.find("StopsDescription")
        el_floors = response.find("Floors")
        el_service = response.find("ServiceDescription")
        el_qualities = response.find("Qualities")

        # Result
        result = self._parse_result(response.find("Result"))

        # seats
        seats = [self._parse_seat(key) for key in response.findall("Seats")]

        # stops
        stops = dict()
        stops["origin"] = el_stops.find("OrigenDesc").text
        stops["origin_address"] = el_stops.find("OrigenDir").text
        stops["destination"] = el_stops.find("DestinoDesc").text
        stops["destination_address"] = el_stops.find("DestinoDir").text

        # service
        service = dict()
        service["company"] = el_service.find("Empresa").text
        service["departure"] = el_service.find("Fecha").text
        service["arrival"] = el_service.find("FechaLlegada").text

        # floors
        floors = dict()
        floors["name"] = el_floors.find("Name").text
        floors["title"] = el_floors.find("Title").text
        floors["rows"] = el_floors.find("Rows").text
        floors["cols"] = el_floors.find("Cols").text

        # qualities
        qualities = dict()
        qualities["code"] = el_qualities.find("Codigo").text.strip()
        qualities["description"] = el_qualities.find("Descripcion").text.strip()

        data["result"] = result
        data["stops"] = stops
        data["service"] = service
        data["floors"] = floors
        data["qualities"] = qualities
        data["seats"] = seats

        return data

    def prepare_sale(self, service_id, seats):

        context = dict()
        context["service_id"] = service_id
        context["seats"] = seats
        seats_xml = render_to_string("trips/seats.xml", context)

        logger.info("seats_xml:%s" % seats_xml)

        response = self.client.service.PrepareSale_Extended(
            self.web_id,
            self.user,
            self.password,
            service_id,
            seats_xml,
            self.connection_id,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        elements = [self._parse_element(key) for key in response.findall("Elements")]
        countries = [self._parse_country(key) for key in response.findall("Countries")]
        document_types = [
            self._parse_document_types(key) for key in response.findall("DocumentTypes")
        ]
        tax_id = [self._parse_tax_id(key) for key in response.findall("IdTributaria")]
        tax_category = [
            self._parse_tax_category(key) for key in response.findall("CondImpositiva")
        ]
        civil_states = [
            self._parse_civil_states(key) for key in response.findall("CivilStates")
        ]

        result = self._parse_result(response.find("Result"))

        data = dict()
        data["guid"] = response.find("Operation").find("GUID").text.strip()
        data["seats"] = elements
        data["countries"] = countries
        data["document_types"] = document_types
        data["tax_id"] = tax_id
        data["tax_category"] = tax_category
        data["civil_states"] = civil_states
        data["result"] = result

        return data

    def get_price(self, service_id, passengers: list[dict]):
        """
        Calculates the final price to be charged based on seats and payment types.
        """

        for p in passengers:
            p["nationality_id"] = self._get_nationality_id(p.get("nationality"))
            p["document_type_id"] = self._get_document_type_id(p.get("document_type"))
            p["residential_id"] = 1

        context = dict()
        context["service_id"] = service_id
        context["passengers"] = [
            {
                "label": 19,
                "amount": 0,
                "first_name": "Inderpal",
                "last_name": "Singh",
                "document_type_id": 1,
                "document_number": random.randint(1000000, 9999999),
                "nationality_id": 10,
                "residential_id": 1,
            },
            {
                "label": 20,
                "amount": 0,
                "first_name": "Harjinder",
                "last_name": "Kaur",
                "document_type_id": 1,
                "document_number": random.randint(1000000, 9999999),
                "nationality_id": 6,
                "residential_id": 1,
            },
        ]

        passengers_xml = render_to_string("trips/get_computed_rates.xml", context)

        logger.info("passengers_xml:%s" % passengers_xml)

        response = self.client.service.GetComputedRates(
            self.web_id,
            self.user,
            self.password,
            service_id,
            passengers_xml,
            self.connection_id,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        element_tags = response.findall("Elements")
        payment_tags = response.findall("Payments")

        elements = [self._parse_price_element(key) for key in element_tags]
        payments = [self._parse_payment(key) for key in payment_tags]
        result = self._parse_result(response.find("Result"))

        data = dict()
        data["elements"] = elements
        data["payments"] = payments
        data["result"] = result

        return data

    def complete_sale(self, service_id, order, guid):
        """
        Confirms a sale and returns tickets.
        Call this when you get payment confirmation from your payment processor via webhook.


        Incomplete - Remove hardcoded dict
        """
        context = dict()
        context["service_id"] = service_id
        context["seats"] = [
            {
                "service_id": 1,
                "label": 20,
                "amount": 550044.0,
                "first_name": "Inderpal",
                "last_name": "Singh",
                "date_of_birth": "1955-02-02",
                "gender": "M",
                "document_type_id": 1,
                "document_number": random.randint(1000000, 9999999),
                "nationality_id": 2,
                "residential_id": 1,
                "tax_id": 2,
                "tax_id_number": 20956028230,
                "tax_category": 1,
                "phone_number": 224327,
                "email": "inderpal@email.com",
            },
        ]

        order_xml = render_to_string("trips/order.xml", context)

        logger.info("order_xml: %s" % order_xml)

        response = self.client.service.CompleteSale_Extended(
            self.web_id,
            self.user,
            self.password,
            service_id,
            order_xml,
            self.connection_id,
            guid,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        result = self._parse_result(response.find("Result"))
        details = self._parse_sale_details(response.find("SaleDataDetails"))
        items = [
            self._parse_sale_item(item) for item in response.findall("SaleDataItems")
        ]

        data = dict()
        data["result"] = result
        data["details"] = details
        data["items"] = items
        return data

    def get_categories(self, company_id, origin, destination):
        """
        For an (origin, destination) pair find all types of offerings for a particular company.
        These are typically the types of seats in a bus.

        # Incomplete
        # This method call doesn't work!
        """

        response = self.client.service.FindServerQualityOpen(
            self.web_id,
            self.user,
            self.password,
            company_id,
            origin,
            destination,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        return response

    def release_seats(self, guid):
        """
        Release seats that were kept on hold for an incomplete purchase.
        We need to run this typically when a session is expired.
        # Incomplete
        """

        response = self.client.service.UnlockSeats_Extended(
            self.web_id, self.user, self.password, guid, self.connection_id, self.key
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        return response

    def check_status(self, guid):
        """
        Check the current status of a transaction.
        """

        response = self.client.service.GetResultTransaction(
            self.web_id, self.user, self.password, guid, self.key
        )
        logger.info(etree.tostring(response, pretty_print=True).decode())

        result = self._parse_result(response.find("Result"))
        operation = self._parse_operation(response.find("Operation"))
        tickets = [self._parse_ticket(key) for key in response.findall("Tickets")]

        data = dict()
        data["result"] = result
        data["operation"] = operation
        data["tickets"] = tickets

        return data

    def check_tickets(self, ticket_id):
        """
        Gives details about a ticket whether confirmed or refunded.

        This API call is weird as it takes all params as xml unlike all others.
        Also it returns raw xml as a response so we parse and convert it to a dict.
        """

        ticket_xml = f"""
        <Parametros>
            <WebAgenciaId>{self.web_agency_id}</WebAgenciaId>
            <IdTx>0</IdTx>
            <MCIdVentaDetalle>{ticket_id}</MCIdVentaDetalle>
            <UserName>{self.user}</UserName>
            <Password>{self.password}</Password>
            <Key>{self.key}</Key>
        </Parametros>"""

        logger.info("ticket_xml:%s" % ticket_xml)

        xml = self.client.service.GetInfoPasaje(ticket_xml)

        response = etree.fromstring(xml)
        logger.info(etree.tostring(response, pretty_print=True).decode())

        data = dict()

        data["status"] = self._parse_ticket_status(response.find("Estado"))
        data["details"] = self._parse_ticket_details(response.find("Datos"))

        return data

    def refund(self, ticket_id, retention_pct):
        """
        Do a refund.

        `retention_pct`: How much percentage of ticket amound shall we keep?
        Eg: if amount = 150, retention_pct = 10 means we keep 10% of 150 and give back 90%

        Unlike other methods this method also takes all params as xml and returns raw xml.
        """

        refund_xml = f"""
        <Parametros>
            <WebAgenciaId>{self.web_agency_id}</WebAgenciaId>
            <IdTx>0</IdTx>
            <MCIdVentaDetalle>{ticket_id}</MCIdVentaDetalle>
            <UserName>{self.user}</UserName>
            <Password>{self.password}</Password>
            <Key>{self.key}</Key>
            <Conexion>{self.connection_id}</Conexion>
            <DevEspecial>1</DevEspecial>
            <DevEspecialMonto>0</DevEspecialMonto>
            <DevEspecialRetencion>{retention_pct}</DevEspecialRetencion>
        </Parametros>"""

        logger.info("refund_xml:%s" % refund_xml)

        xml = self.client.service.DevolucionGrabar(refund_xml)
        response = etree.fromstring(xml)
        logger.info(etree.tostring(response, pretty_print=True).decode())

        data = dict()

        data["status"] = self._parse_refund_status(response.find("Estado"))
        data["details"] = self._parse_refund_details(response.find("Datos"))

        return data

    def end_session(self):
        response = self.client.service.EndSession(
            self.web_id, self.user, self.password, self.connection_id, self.key
        )
        is_ok = response.xpath("//IsOk")[0].text
        has_warnings = response.xpath("//HasWarnings")[0].text

        self.connection_id = None

        logger.info("is_ok?:%s" % is_ok)
        logger.info("has_warnings?:%s" % has_warnings)

        return is_ok

    def get_stops(self, stop_id=0, web_agency_id=0):
        """
        Handy method to get all stops that are approved for an agencia mayorista.

        web_agency_id: refers to the `agencia mayorista` for which a `agencia minorista` would like to
        know which stops are approved (homolgadas)

        Default values of 0 for both stop_id and web_agency_id pulls in all stops with their details.
        """

        stops_xml = f"<Params><StopId>{stop_id}</StopId><WebAgenciaId>{web_agency_id}</WebAgenciaId></Params>"

        response = self.client.service.Execute(
            "Designers.GetStopsWithFullInfo", stops_xml
        )
        response = response["_value_1"]["_value_1"]

        return [x.get("Stops") for x in response if "Stops" in x]

    def get_all_companies(self, web_id=0):
        params_xml = f"<Params><WebId>{web_id}</WebId></Params>"

        response = self.client.service.Execute(
            "Designers.GetAllCompaniesDetailsByWeb", params_xml
        )
        response = response["_value_1"]["_value_1"]
        return [x.get("CompaniesDetails") for x in response if "CompaniesDetails" in x]

    def _parse_service(self, key):
        data = dict()

        data["service_id"] = key.xpath("//Servicio/@idServicio")[0]
        data["departure"] = self._parse_datetime(value=key.find("HoraSalida").text)
        data["arrival"] = self._parse_datetime(value=key.find("HoraLlegada").text)
        data["seats_available"] = key.find("ButacasLibres").text.split()[1]
        data["can_select_seats"] = key.xpath("//VeTaquilla")[0].text
        data["category"] = key.xpath("//Clase")[0].text
        data["company"] = key.xpath("//Empresa")[0].text
        data["company_id"] = key.find("EmpresaId").text
        data["price"] = round(float(key.find("Precio").text.split()[1]))
        data["price_promotional"] = round(
            float(key.find("TarifaPromo").text.split()[1])
        )
        data["has_discount"] = key.xpath("//TieneDescuento")[0].text
        data["currency_code"] = key.xpath("//MonedaISO")[0].text
        data["is_international"] = key.xpath("//EsInternacional")[0].text

        return data

    def _parse_seat(self, key):
        data = dict()

        data["floor"] = key.find("Floor").text
        data["row"] = key.find("Row").text
        data["col"] = key.find("Col").text
        data["label"] = key.find("Text").text
        data["quality"] = key.find("Quality").text
        data["status"] = key.find("Status").text
        data["is_selectable"] = key.find("Selectable").text
        data["category"] = key.find("Type").text

        return data

    def _parse_stop(self, key):
        data = dict()

        data["id"] = key.get("id").strip().title()
        data["name"] = key.get("localidad").strip().title()
        data["state"] = key.get("provincia").strip().title()
        data["country"] = key.get("pais").strip().title()
        data["arrival"] = key.get("llega").strip()
        data["departure"] = key.get("sale").strip()

        return data

    def _parse_result(self, el):
        result = dict()
        result["is_ok"] = el.find("IsOk").text
        result["has_warnings"] = el.find("HasWarnings").text

        return result

    def _parse_element(self, key):
        data = dict()

        data["id"] = key.find("ID").text
        data["service"] = key.find("Service").text
        data["seat"] = key.find("Element").text
        data["quality"] = key.find("Quality").text
        data["amount"] = key.find("Amount").text
        data["payment_info"] = key.find("PaymentInfo").text
        data["residential_id"] = key.find("ResidentialId").text
        data["nationality_id"] = key.find("NationalityId").text

        return data

    def _parse_price_element(self, key):
        data = dict()

        data["id"] = key.find("ID").text
        data["service"] = key.find("Service").text
        data["seat"] = key.find("Element").text
        data["quality"] = key.find("Quality").text
        data["interest"] = key.find("Interest").text
        data["interest_amount"] = key.find("InterestAmount").text
        data["amount"] = key.find("Amount").text
        data["discount_code"] = key.find("DiscountCode").text
        data["discount_amount"] = key.find("DiscountAmount").text
        data["discount_amount_special"] = key.find("SpecialDiscountAmount").text
        data["payment_info"] = key.find("PaymentInfo").text
        data["residential_id"] = key.find("ResidentialId").text
        data["nationality_id"] = key.find("NationalityId").text
        data["rg3450_amount"] = key.find("RG3450Amount").text
        data["rate_type"] = key.find("RateType").text

        return data

    def _parse_payment(self, key):
        data = dict()

        data["id"] = key.find("ID").text
        data["type"] = key.find("Type").text
        data["amount"] = key.find("Amount").text
        data["entity"] = key.find("Entity").text
        data["number"] = key.find("Number").text
        data["months"] = key.find("Months").text
        data["currency"] = key.find("Currency").text
        data["interest"] = key.find("Interest").text
        data["first_name"] = key.find("FirstName").text
        data["last_name"] = key.find("LastName").text
        data["document"] = key.find("Document").text
        data["phone"] = key.find("Phone").text
        data["commerce"] = key.find("Commerce").text
        data["terminal"] = key.find("Terminal").text
        data["Lot"] = key.find("Lot").text
        data["Coupon"] = key.find("Coupon").text
        data["Authorization"] = key.find("Authorization").text
        data["rg3450_amount"] = key.find("AmountRG3450").text
        data["currency_iso"] = key.find("CurrencyISO").text

        return data

    def _parse_country(self, key):
        data = dict()

        data["id"] = key.find("Id").text
        data["description"] = key.find("Descripcion").text

        return data

    def _parse_document_types(self, key):
        data = dict()

        data["id"] = key.find("Id").text
        data["description"] = key.find("Descripcion").text

        return data

    def _parse_tax_id(self, key):
        data = dict()

        data["id"] = key.find("Id").text
        data["code"] = key.find("Codigo").text
        data["name"] = key.find("Nombre").text

        return data

    def _parse_tax_category(self, key):
        data = dict()

        data["id"] = key.find("Id").text
        data["code"] = key.find("Codigo").text
        data["name"] = key.find("Nombre").text

        return data

    def _parse_civil_states(self, key):
        data = dict()

        data["id"] = key.find("Id").text
        data["description"] = key.find("Descripcion").text
        data["code"] = key.find("EstadoCivilIdMGO").text

        return data

    def _parse_sale_details(self, key):
        data = dict()

        data["origin"] = key.find("sMCNombreParadaOrigen").text
        data["destination"] = key.find("sMCNombreParadaDestino").text
        data["departure"] = key.find("dMCFechaHoraSalida").text
        data["arrival"] = key.find("MCFechahorallegada").text
        data["created"] = key.find("dMCFechaEmision").text
        data["category"] = key.find("CalidadLegalDes").text.strip()
        data["company"] = key.find("EmpTransportista").text.strip()
        data["company_description"] = key.find("EmpTransportistaDes").text.strip()
        data["company_address"] = key.find("EmpresaDomicilio").text.strip()
        data["company_tax_category"] = key.find("EmpresaIVA").text.strip()
        data["company_tax_id"] = key.find("EmpresaCUIT").text.strip()
        data["company_tax_iibb"] = key.find("EmpresaIIBB").text.strip()
        data["company_email"] = key.find("EmpresaMail").text.strip()

        return data

    def _parse_sale_item(self, key):
        data = dict()

        data["ticket_number"] = key.find("Boleto").text
        data["seat"] = key.find("Butaca").text
        data["price_gross"] = key.find("PrecioBruto").text
        data["price_net"] = key.find("PrecioNeto").text
        data["price_net"] = key.find("PrecioNeto").text
        data["currency"] = key.find("MonedaISO").text
        data["first_name"] = key.find("MCPasajeroNombre").text
        data["last_name"] = key.find("MCPasajeroApellido").text
        data["last_name"] = key.find("MCPasajeroApellido").text
        data["document_type"] = key.find("MCPasajeroTipoDocumento").text
        data["document_number"] = key.find("MCPasajeroNumeroDocumento").text
        data["Nationality"] = key.find("MCPasajeroNacionalidad").text
        data["date_of_birth"] = key.find("MCPasajeroFechaNacimiento").text
        data["phone_number"] = key.find("MCPasajeroNumeroTelefono").text
        data["email"] = key.find("MCPasajeroMail").text
        data["gender"] = key.find("MCPasajeroSexo").text
        data["bar_code"] = key.find("TextoEspecial").text
        data["qr_code"] = key.find("TextoQR").text

        return data

    def _parse_operation(self, key):
        data = dict()

        data["guid"] = key.find("GUID").text.strip()
        data["order_id"] = key.find("OperacionId").text.strip()
        data["created"] = key.find("Fecha").text.strip()
        data["error"] = key.find("Error").text.strip()
        data["message"] = key.find("Mensaje").text.strip()

        return data

    def _parse_ticket(self, key):
        data = dict()

        data["seat"] = key.find("Butaca").text.strip()
        data["ticket_number"] = key.find("Boleto").text.strip()
        data["ticket_id"] = key.find("IdVentaDetalle").text.strip()

        return data

    def _parse_ticket_details(self, key):

        data = dict()

        data["company"] = key.find("Empresa").text
        data["trip"] = key.find("Servicio").text.strip()
        data["ticket_number"] = key.find("BoletoMGO").text
        data["origin"] = key.find("OrigenDes").text.strip()
        data["destination"] = key.find("DestinoDes").text.strip()
        data["departure"] = key.find("Embarque").text
        data["seat"] = key.find("Butaca").text
        data["amount"] = key.find("Importe").text
        data["payment_type"] = key.find("FormaPago").text
        data["created"] = key.find("FechaAlta").text
        data["is_open"] = key.find("Abierto").text
        data["is_cancelled"] = key.find("Anulado").text
        data["is_refunded"] = key.find("Devuelto").text
        data["refunded_on"] = key.find("DevFecha").text
        data["refunded_amount"] = key.find("DevImporte").text
        data["refunded_amount_total"] = key.find("DevImporteTotal").text

        return data

    def _parse_ticket_status(self, key):
        data = dict()

        data["code"] = key.find("Codigo").text.strip()
        data["description"] = key.find("Descripcion").text.strip()

        return data

    def _parse_refund_status(self, key):
        return self._parse_ticket_status(key)

    def _parse_refund_details(self, key):
        data = dict()

        data["refund_amount"] = key.find("MontoDevuelto").text
        data["boarding_tax"] = key.find("TasaEmbarque").text
        data["refund_amount_total"] = key.find("TotalDevuelto").text

        return data

    def _parse_datetime(self, value):
        """
        Parses the custom string datetime of the api into an aware django datetime.
        """

        dt = datetime.strptime(value, "%d/%m/%Y %H:%M")
        return timezone.make_aware(dt)

    def _get_nationality_id(self, country_code: str):
        """
        Find the nationality id based on Prosys codes. If nationality not in list
        then return Argentina.
        """

        code_map = {
            "AR": "2",
            "BO": 10,
            "BR": "5",
            "CL": "6",
            "CO": "18",
            "EC": "16",
            "PY": "9",
            "PE": "13",
            "UY": "14",
            "VE": "15",
        }

        return code_map.get(country_code, "2")

    def _get_document_type_id(self, code: str):
        """
        Returns the document type id as per prosys mapping. This method needs improvement
        as it doesn't cover all cases perfectly.

        For doc types not in the map below we return DNI.
        """

        doc_map = {
            "DNI": "1",
            "CEDULA": "2",
            "PASSPORT": "3",
            "LE": "5",
            "LC": "7",
            "CUIT": "4",
            "RUT": "4",
            "NIE": "4",
        }

        return doc_map.get(code, "1")

    def __repr__(self):
        return "Prosys Client 👋"
