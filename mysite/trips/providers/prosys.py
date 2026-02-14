import json
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

from .exceptions import (
    InvalidCompleteSale,
    InvalidCompleteSaleInsurance,
    InvalidEndSession,
    InvalidPaymentsType,
    InvalidPrepareSale,
    InvalidPrepareSaleInsurance,
    InvalidRefund,
    InvalidTransaction,
)


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
            self.client = Client(
                self.url, transport=transport, plugins=[self.history]
            )

        except requests.exceptions.ConnectionError as e:
            logger.warn("Prosys ConnectionError:%s" % e)
            mail_admins(
                "Prosys ConnectionError", f"Connection Id:{connection_id}"
            )
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
        session = response.find("SessionInformation")
        result = response.find("Result")

        connection_id = session.find("ConnectionId").text
        is_ok = result.find("IsOk").text
        has_warnings = result.find("HasWarnings").text

        logger.info("connecton_id:%s" % connection_id)
        logger.info("is_ok?:%s" % is_ok)
        logger.info("has_warnings?:%s" % has_warnings)

        return connection_id

    def search(self, origin, destination, departure):
        origin, destination = (
            STOPS_MAP.get(origin, {}),
            STOPS_MAP.get(destination, {}),
        )

        # added dummy id's below for which we don't have any map. Remove them later
        origin_id = origin.get("IdParada", 123)
        destination_id = destination.get("IdParada", 456)

        logger.info(
            "searching from:%s to:%s on:%s"
            % (origin_id, destination_id, departure)
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
        """
        Loads the seat map for a service.
        """

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
        qualities["description"] = el_qualities.find(
            "Descripcion"
        ).text.strip()

        data["result"] = result
        data["stops"] = stops
        data["service"] = service
        data["floors"] = floors
        data["qualities"] = qualities
        data["seats"] = seats

        return data

    def get_service_with_seat_map(self, service_id):
        """
        Custom method to build a processed seat map to render in django template.
        """

        seat_map = dict()

        # Get service details from api
        service = self.get_service(service_id)
        seats = service.get("seats")

        # Find floors in result
        floors = sorted(set([x["floor"] for x in seats]))

        # For each floor build empty rows of 15 no. each
        for floor in floors:
            seat_map[floor] = [[] for _ in range(15)]

        # Populate each empty row with relevant seats
        for seat in service.get("seats"):
            index = int(seat.get("row"))
            floor = seat.get("floor")

            seat_map[floor][index].append(seat)

        # Remove all empty rows that don't have any seats
        for floor in floors:
            rows = seat_map[floor]
            rows = [row for row in rows if row]
            seat_map[floor] = rows

        service["seat_map"] = seat_map

        return service

    def get_payments_type_by_service(self, service_id):
        """
        Gets all the payment types that a service accepts for booking.
        """
        data = dict()

        response = self.client.service.GetPaymentsTypeByService(
            self.web_id,
            self.user,
            self.password,
            service_id,
            self.connection_id,
            self.key,
        )

        logger.debug(etree.tostring(response, pretty_print=True).decode())
        result = self._parse_result(response.find("Result"))

        if result["is_ok"] == "false":
            data["errors"] = self._parse_errors(response.find("Errors"))

            data_json = json.dumps(data, indent=4, ensure_ascii=False)

            subject = "Payments Types Error"
            message = f"Data:{data_json}"

            mail_admins(subject=subject, message=message)

            err = data.get("errors").get("description")

            raise InvalidPaymentsType(err)

        payments_type = [
            self._parse_payments_type(key)
            for key in response.findall("PaymentsTypes")
        ]
        data["result"] = result
        data["payments_type"] = payments_type

        return data

    def prepare_sale(self, service_id, seats):

        context = dict()
        context["service_id"] = service_id
        context["seats"] = seats
        seats_xml = render_to_string("trips/prepare_sale.xml", context)

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

        result = self._parse_result(response.find("Result"))

        data = dict()
        data["result"] = result

        if result["is_ok"] == "false":
            data["errors"] = self._parse_errors(response.find("Errors"))

            data_json = json.dumps(data, indent=4, ensure_ascii=False)
            context_json = json.dumps(context, indent=4, ensure_ascii=False)

            subject = "PrepareSale Error"
            message = f"Context:{context_json}\nData:{data_json}"

            mail_admins(subject=subject, message=message)

            err = data.get("errors").get("description")

            raise InvalidPrepareSale(err)

        elements = [
            self._parse_element(key) for key in response.findall("Elements")
        ]
        countries = [
            self._parse_country(key) for key in response.findall("Countries")
        ]
        document_types = [
            self._parse_document_types(key)
            for key in response.findall("DocumentTypes")
        ]
        tax_id = [
            self._parse_tax_id(key) for key in response.findall("IdTributaria")
        ]
        tax_category = [
            self._parse_tax_category(key)
            for key in response.findall("CondImpositiva")
        ]
        civil_states = [
            self._parse_civil_states(key)
            for key in response.findall("CivilStates")
        ]

        data["guid"] = response.find("Operation").find("GUID").text.strip()
        data["seats"] = elements
        data["countries"] = countries
        data["document_types"] = document_types
        data["tax_id"] = tax_id
        data["tax_category"] = tax_category
        data["civil_states"] = civil_states

        return data

    def prepare_sale_insurance(self, service_id):
        response = self.client.service.PrepareSale_Insurance(
            self.web_id,
            self.user,
            self.password,
            service_id,
            self.connection_id,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        result = self._parse_result(response.find("Result"))

        data = dict()
        data["result"] = result

        if result["is_ok"] == "false":
            errors = self._parse_errors(response.find("Errors"))
            data["errors"] = errors
            data_json = json.dumps(data, indent=4, ensure_ascii=False)

            subject = "PrepareSaleInsurance Error"
            message = f"ServiceId:{service_id}\nData:{data_json}"

            logger.warn(subject)
            logger.warn(message)

            mail_admins(subject=subject, message=message)

            raise InvalidPrepareSaleInsurance(errors.get("description"))

        insurance_info = self._parse_insurance_info(
            response.find("Seguros_Info")
        )

        countries = [
            self._parse_country(key) for key in response.findall("Countries")
        ]
        document_types = [
            self._parse_document_types(key)
            for key in response.findall("DocumentTypes")
        ]
        tax_id = [
            self._parse_tax_id(key) for key in response.findall("IdTributaria")
        ]
        tax_category = [
            self._parse_tax_category(key)
            for key in response.findall("CondImpositiva")
        ]
        civil_states = [
            self._parse_civil_states(key)
            for key in response.findall("CivilStates")
        ]

        data["insurance_info"] = insurance_info
        data["countries"] = countries
        data["document_types"] = document_types
        data["tax_id"] = tax_id
        data["tax_category"] = tax_category
        data["civil_states"] = civil_states

        return data

    def get_price(self, service_id, seats):
        """
        Calculates the final price to be charged based on seats and payment types.

        Eg: of passengers argument
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
        """

        passengers = [
            {
                "label": label,
                "amount": 0,
                "first_name": "Inderpal",
                "last_name": "Singh",
                "document_type_id": 1,
                "document_number": random.randint(1000000, 9999999),
                "nationality_id": 10,
                "residential_id": 1,
            }
            for label in seats
        ]

        context = dict()
        context["service_id"] = service_id
        context["passengers"] = passengers

        passengers_xml = render_to_string(
            "trips/get_computed_rates.xml", context
        )

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
        data["seats"] = elements
        data["payments"] = payments
        data["result"] = result

        return data

    def complete_sale(self, service_id, guid, passengers):
        """
        Confirms a sale and returns tickets.
        Call this when you get payment confirmation from your payment processor via webhook.

        Note: This method is called by the webhook when we have received confirmed payment
        from the user and we are supposed to complete the sale and confirm the order.

        So failure of execution of this method is very critical to business
        and it should be reported immmediately typically via email.
        """

        for p in passengers:
            p["amount"] = float(p.get("amount"))
            p["document_type_id"] = self._get_document_type_id(
                p.get("document_type")
            )
            p["nationality_id"] = self._get_nationality_id(
                p.get("nationality")
            )
            p["residential_id"] = 1
            p["tax_id"] = 2
            p["tax_id_number"] = 9876543
            p["tax_category"] = 1
            p["email"] = "passenger@email.com"

        context = dict()
        context["service_id"] = service_id
        context["seats"] = passengers

        logger.info("context:%s" % context)

        order_xml = render_to_string("trips/complete_sale.xml", context)

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

        data = dict()
        data["result"] = result

        if result["is_ok"] == "false":
            errors = self._parse_errors(response.find("Errors"))
            data["errors"] = errors
            passengers_json = json.dumps(
                passengers, indent=4, ensure_ascii=False
            )
            data_json = json.dumps(data, indent=4, ensure_ascii=False)

            subject = f"CompleteSale Error Guid:{guid}"
            message = f"Guid:{guid}\nServiceId:{service_id}\nPassengers:{passengers_json}\nData:{data_json}"

            logger.warn(subject)
            logger.warn(message)

            mail_admins(subject=subject, message=message)

            raise InvalidCompleteSale(errors.get("description"))

        details = self._parse_sale_details(response.find("SaleDataDetails"))
        items = [
            self._parse_sale_item(item)
            for item in response.findall("SaleDataItems")
        ]

        data["details"] = details
        data["items"] = items

        return data

    def complete_sale_insurance(self, service_id, insurance_amount):
        """
        Incomplete method and WIP

        Completes the sale of an insurance typically for a "child" and associate
        it with a ticket.
        Veer this method is very similar to a the complete sale method.

        Initially our search() and prepare_sale_insurance() methods need to be called
        from the UI
        prepare_sale_insurance gives the insurance amount which we need to pass here
        The response is very similar to complete_sale() method just that the insurance
        amounts are very small!

        This is an experimental method and we need to decide later if we wish to habilitate
        this on the frontend.

        # Todo: Add passenger details to context and template
        """

        context = dict()
        context["service_id"] = service_id
        context["insurance_amount"] = insurance_amount
        insurance_xml = render_to_string(
            "trips/complete_sale_insurance.xml", context
        )

        logger.info("insurance_xml: %s" % insurance_xml)

        response = self.client.service.CompleteSale_Insurance(
            self.web_id,
            self.user,
            self.password,
            service_id,
            insurance_xml,
            self.connection_id,
            self.key,
        )

        logger.info(etree.tostring(response, pretty_print=True).decode())

        result = self._parse_result(response.find("Result"))

        data = dict()
        data["result"] = result

        if result["is_ok"] == "false":
            errors = self._parse_errors(response.find("Errors"))

            data["errors"] = errors
            data_json = json.dumps(data, indent=4, ensure_ascii=False)

            subject = "CompleteSaleInsurance Error"
            message = f"ServiceId:{service_id}\nData:{data_json}"

            logger.warn(subject)
            logger.warn(message)

            mail_admins(subject=subject, message=message)

            raise InvalidCompleteSaleInsurance(errors.get("description"))

        details = self._parse_sale_details(response.find("SaleDataDetails"))
        items = [
            self._parse_sale_item(item)
            for item in response.findall("SaleDataItems")
        ]

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
            self.web_id,
            self.user,
            self.password,
            guid,
            self.connection_id,
            self.key,
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

        operation_el = response.find("Operation")

        if operation_el is None:
            raise InvalidTransaction(
                "Could not find the transaction. Invalid guid"
            )

        operation = self._parse_operation(operation_el)
        tickets = [
            self._parse_ticket(key) for key in response.findall("Tickets")
        ]

        data = dict()
        data["result"] = result
        data["operation"] = operation
        data["tickets"] = tickets

        return data

    def check_ticket(self, ticket_id):
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

    def get_tickets(self, guid):
        """
        Wrapper method that checks the status of an order and pulls the ticket ids.
        For each ticket id we then pull the current ticket status.
        """
        tickets = []

        status = self.check_status(guid=guid)

        for ticket in status["tickets"]:
            details = self.check_ticket(ticket["ticket_id"]).get("details")
            data = ticket | details
            tickets.append(data)

        return tickets

    def refund(self, ticket_id, retention_pct=0):
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
        status = self._parse_refund_status(response.find("Estado"))

        data["status"] = status

        if status["code"] != "0":
            # For invalid refund status code is non-zero
            raise InvalidRefund(status["description"])

        data["details"] = self._parse_refund_details(response.find("Datos"))

        return data

    def end_session(self):
        """
        Ends a session with the API.
        """

        response = self.client.service.EndSession(
            self.web_id, self.user, self.password, self.connection_id, self.key
        )

        logger.debug(etree.tostring(response, pretty_print=True).decode())

        result = self._parse_result(response.find("Result"))

        data = dict()
        data["result"] = result

        if result["is_ok"] == "false":
            errors = self._parse_errors(response.find("Errors"))
            data["errors"] = errors
            data_json = json.dumps(data, indent=4, ensure_ascii=False)

            subject = "Invalid EndSession"
            message = f"Data:{data_json}"

            mail_admins(subject=subject, message=message)

            raise InvalidEndSession(errors.get("description"))

        self.connection_id = None

        return data

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
        return [
            x.get("CompaniesDetails")
            for x in response
            if "CompaniesDetails" in x
        ]

    def _parse_service(self, key):
        data = dict()

        data["service_id"] = key.get("idServicio")
        data["service_code"] = key.find("CodigoServicio").text
        data["departure"] = self._parse_datetime(
            value=key.find("HoraSalida").text
        )
        data["arrival"] = self._parse_datetime(
            value=key.find("HoraLlegada").text
        )
        # data["seats_available"] = key.find("ButacasLibres").text.split()[1]
        data["seats_available"] = key.find("ButacasLibres").text
        data["can_select_seats"] = key.find("VeTaquilla").text
        data["category"] = key.find("Clase").text
        data["company"] = key.find("Empresa").text
        data["company_id"] = key.find("EmpresaId").text
        data["transporter"] = key.find("EmpresaTransportista").text
        data["transporter_id"] = key.find("EmpresaTransportistaId").text
        # data["price"] = round(float(key.find("Precio").text.split()[1]))
        # data["price_promotional"] = round(
        #     float(key.find("TarifaPromo").text.split()[1])
        # )
        data["price"] = key.find("Precio").text
        data["price_promotional"] = key.find("TarifaPromo").text
        data["has_discount"] = key.find("TieneDescuento").text
        data["currency_code"] = key.find("Moneda").text
        data["currency_code_iso"] = key.find("MonedaISO").text
        data["is_international"] = key.find("EsInternacional").text

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

        data["id"] = key.get("id").strip()
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

    def _parse_errors(self, key):
        """
        If result is not ok from api then Errors are returned in response.
        Eg xml is like this...

        <Errors>
            <Code>225</Code>
            <Description>Las butacas preparadas no corresponden a las butacas enviadas.</Description>
            <Tag/>
            <Severity>1</Severity>
        </Errors>
        """

        data = dict()

        data["code"] = key.find("Code").text
        data["description"] = key.find("Description").text
        data["tag"] = key.find("Tag").text
        data["severity"] = key.find("Severity").text

        return data

    def _parse_payments_type(self, key):
        data = dict()

        data["code"] = key.find("Codigo").text
        data["description"] = key.find("Descripcion").text.strip()

        return data

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
        data["discount_amount_special"] = key.find(
            "SpecialDiscountAmount"
        ).text
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

    def _parse_insurance_info(self, key):
        data = dict()

        data["insurance_amount"] = key.find("ImporteSeguro").text
        data["max_age"] = key.find("EdadMaximaVenta").text
        data["associate"] = key.find("Asociar").text
        data["quantity"] = key.find("CantidadAsociar").text
        data["rg3450_amount"] = key.find("RG3450Amount").text
        data["rg3450_not_charge_foreigners"] = key.find(
            "RG3450NoCobraAExtranjeros"
        ).text
        data["currency_code"] = key.find("MonedaISO").text

        return data

    def _parse_sale_details(self, key):
        data = dict()

        data["origin"] = key.find("sMCNombreParadaOrigen").text
        data["origin_code"] = key.find("nMCIdParadaOrigen").text
        data["destination"] = key.find("sMCNombreParadaDestino").text
        data["destination_code"] = key.find("nMCIdParadaDestino").text
        data["service"] = key.find("sMCCodigoServicio").text
        data["category"] = key.find("sMCCalidadServicio").text
        data["insurance"] = key.find("sMCPolizaSeguro").text
        data["message"] = key.find("sMCMensajePasajero").text
        data["departure"] = key.find("dMCFechaHoraSalida").text
        data["arrival"] = key.find("MCFechahorallegada").text
        data["created"] = key.find("dMCFechaEmision").text
        data["category_description"] = key.find("CalidadLegalDes").text
        data["company_code"] = key.find("EmpTransportista").text
        data["company"] = key.find("EmpTransportistaDes").text
        data["company_address"] = key.find("EmpresaDomicilio").text
        data["company_tax_category"] = key.find("EmpresaIVA").text
        data["company_tax_id"] = key.find("EmpresaCUIT").text
        data["company_tax_iibb"] = key.find("EmpresaIIBB").text
        data["company_email"] = key.find("EmpresaMail").text

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
        data["nationality"] = key.find("MCPasajeroNacionalidad").text
        data["date_of_birth"] = key.find("MCPasajeroFechaNacimiento").text
        data["phone_number"] = key.find("MCPasajeroNumeroTelefono").text
        data["email"] = key.find("MCPasajeroMail").text
        data["gender"] = key.find("MCPasajeroSexo").text
        data["bar_code"] = key.find("TextoEspecial").text
        data["qr_code"] = key.find("TextoQR").text

        return data

    def _parse_operation(self, key):
        data = dict()

        data["guid"] = key.find("GUID").text
        data["order_id"] = key.find("OperacionId").text
        data["created"] = key.find("Fecha").text
        data["error"] = key.find("Error").text
        data["message"] = key.find("Mensaje").text

        return data

    def _parse_ticket(self, key):
        data = dict()

        data["seat"] = key.find("Butaca").text
        data["ticket_number"] = key.find("Boleto").text
        data["ticket_id"] = key.find("IdVentaDetalle").text

        return data

    def _parse_ticket_details(self, key):

        data = dict()

        data["company"] = key.find("Empresa").text
        data["trip"] = key.find("Servicio").text
        data["ticket_number"] = key.find("BoletoMGO").text
        data["origin"] = key.find("OrigenDes").text
        data["destination"] = key.find("DestinoDes").text
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

        # Generate this key based on derived logic of other data for a ticket
        # Very handy later
        data["is_refundable"], data["retention_pct"] = self._get_refund_status(
            key
        )

        return data

    def _get_refund_status(self, key):
        """
        Calculate the refund status and retention percentage based on a departure.

        TODO: Implement for servicios provinciales

        departure datetime string from api is of kind "07/10/2025 - 11:20"
        delta = (departure - now)

        Refund Rules for Servicios Nacionales:
            48hs < delta => 10%
            24hs < delta < 48hs => 20%
            1h < delta < 24hs => 30%
            delta < 1h => 0%
        """

        departure = key.find("Embarque").text
        already_refunded = key.find("Devuelto").text

        print(f"already_refunded:{already_refunded}")

        dt = datetime.strptime(departure, "%m/%d/%Y - %H:%M")
        departure = timezone.make_aware(dt)
        now = timezone.localtime()

        td = departure - now
        hours = td.total_seconds() / 3600

        logger.info("departure:%s" % departure)
        logger.info("now:%s" % now)
        logger.info("hours before departure:%s" % hours)

        # Calculate retention_pct based on departure and now
        if hours > 48:
            retention_pct = 10

        elif 24 < hours <= 48:
            retention_pct = 20

        elif 1 < hours <= 24:
            retention_pct = 30

        else:
            retention_pct = 0

        is_refundable = (already_refunded is None) and (retention_pct > 0)

        return is_refundable, retention_pct

    def _parse_ticket_status(self, key):
        data = dict()

        data["code"] = key.find("Codigo").text
        data["description"] = key.find("Descripcion").text

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
