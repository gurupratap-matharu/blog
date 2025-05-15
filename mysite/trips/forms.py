import json
import logging
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.http.request import QueryDict
from django.utils.translation import gettext_lazy as _

logger = logging.Logger(__name__)


class TripSearchForm:
    """
    Dummy class used to validate the searcxh query received from the homepage trip search form.

    We are not using django form for the main form as we don't know how to couple it
    with
        - autocomplete Js to show dynamic search results for locations
        - flatpickr to launch calendar for departure and return

    But we do need to validate the form one way or the other.
    This class does just that.
    """

    VALID_TRIP_TYPES = ("round_trip", "one_way")
    VALID_NUM_PASSENGERS = 10

    def __init__(self, data: QueryDict | dict[str, list[str]]):
        self.data = data or {}

    def validate(self):
        logger.info("validating search form...")

        origin = self.clean_origin()
        destination = self.clean_destination()
        departure = self.clean_departure()
        self.clean_return()
        self.clean_num_passengers()
        self.clean_trip_type()

        return origin, destination, departure

    def clean_origin(self):
        """Only allow origins present in our database"""

        origin = self.data.get("origin")

        if isinstance(origin, list):
            origin = origin[0]

        if not origin:
            raise ValidationError(_("Orígen es invalido"), code="invalid")

        # veer add logic to validate origin code

        return origin

    def clean_destination(self):
        """Only allow destinations present in our database"""

        destination = self.data.get("destination")

        if isinstance(destination, list):
            destination = destination[0]

        if not destination:
            raise ValidationError(_("Destino es invalido"), code="invalid")

        # veer add logic to validation destination code

        return destination

    def clean_departure(self):
        """
        Make sure departure is not in the past and is supplied
        """

        departure = self.data.get("departure")

        if isinstance(departure, list):
            departure = departure[0]

        if not departure:
            raise ValidationError(_("Fecha de ida es invalida"), code="invalid")

        self.departure_date = datetime.strptime(departure, "%d-%m-%Y").date()

        if self.departure_date < datetime.today().date():
            raise ValidationError(
                _("Fecha de ida:%(value)s no puede ser en el pasado"),
                code="invalid",
                params={"value": self.departure_date},
            )

        return self.departure_date

    def clean_return(self):
        """
        Don't allow return date to be less than departure date
        Note: Return date is optional in our form.
        """

        today = datetime.today().date()
        departure_date = self.departure_date
        return_date = self.data.get("return")

        if isinstance(return_date, list):
            return_date = return_date[0]

        if not return_date:
            return

        return_date = datetime.strptime(return_date, "%d-%m-%Y").date()

        if (return_date < departure_date) or (return_date < today):
            raise ValidationError(
                _("Fecha de vuelta:%(value)s es invalida"),
                code="invalid",
                params={"value": return_date},
            )

        return return_date

    def clean_trip_type(self):
        """
        Only allow trip types to be in self.VALID_TRIP_TYPES
        """

        trip_type = self.data.get("trip_type")

        if not trip_type:
            raise ValidationError(_("Tipo de viaje es invalido"), code="invalid")

        if isinstance(trip_type, list):
            trip_type = trip_type[0]

        if trip_type not in self.VALID_TRIP_TYPES:
            raise ValidationError(
                _("Tipo de viaje:%(value)s es invalido"),
                code="invalid",
                params={"value": trip_type},
            )

    def clean_num_passengers(self):
        """
        Only allow num of passengers to be <= self.VALID_NUM_PASSENGERS
        """

        num_of_passengers = self.data.get("num_of_passengers")

        if not num_of_passengers:
            raise ValidationError(_("Número de pasajeros es invalido"), code="invalid")

        if isinstance(num_of_passengers, list):
            num_of_passengers = num_of_passengers[0]

        num_of_passengers = int(num_of_passengers)

        if num_of_passengers < 1 or num_of_passengers > self.VALID_NUM_PASSENGERS:
            raise ValidationError(
                _("Número de pasajeros:%(value)s es invalido"),
                code="invalid",
                params={"value": num_of_passengers},
            )

    def __repr__(self):
        return json.dumps(self.data)


class SeatForm(forms.Form):
    seats = forms.CharField(max_length=20, widget=forms.HiddenInput)
