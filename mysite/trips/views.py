import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from trips.forms import SeatForm, TripSearchForm
from trips.providers.prosys import Prosys

logger = logging.getLogger(__name__)


class TripSearchView(TemplateView):
    template_name = "trips/trip_list.html"
    form_class = TripSearchForm
    error_message = _("Probar de vuelta")

    def get(self, request, *args, **kwargs):
        """
        Validate the search query here before proceeding forward.
        If valid then add to session else redirect to home with relevant message.
        """

        q = request.GET

        try:
            form = self.form_class(q)
            self.origin, self.destination, self.departure = form.validate()

        except Exception as e:
            messages.info(request, f"{e.messages[0]}! {self.error_message}")
            return redirect("/")

        logger.info("search query:%s..." % q)
        request.session["q"] = q

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        results = self.search()
        context["origin"] = results["origin"]
        context["destination"] = results["destination"]
        context["trips"] = results["trips"]

        return context

    def search(self):
        session = self.request.session
        obj = Prosys(connection_id=session.get("connection_id"))
        session["connection_id"] = obj.connection_id
        results = obj.search(self.origin, self.destination, self.departure)

        return results


class TripDetailView(TemplateView):
    template_name = "trips/trip_detail.html"
    session_keys = ("q", "connection_id")

    def dispatch(self, request, *args, **kwargs):
        """
        Verify that session is valid with all keys else redirect to home.
        """

        if not all(k in request.session for k in self.session_keys):
            messages.info(request, settings.SESSION_EXPIRED_MESSAGE)
            return redirect("/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["route"] = self.get_route(service_id=kwargs.get("service_id"))
        return context

    def get_route(self, service_id):
        session = self.request.session
        obj = Prosys(connection_id=session.get("connection_id"))
        route = obj.get_route(service_id)
        return route


class SeatsView(FormView):
    template_name = "trips/seats.html"
    form_class = SeatForm
    success_url = reverse_lazy("orders:order-create")
    session_keys = ("q", "connection_id")

    def dispatch(self, request, *args, **kwargs):
        """
        Verify that session is valid with all keys else redirect to home.
        """

        if not all(k in request.session for k in self.session_keys):
            messages.info(request, settings.SESSION_EXPIRED_MESSAGE)
            return redirect("/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        service_id = self.kwargs.get("service_id")
        context["trip"] = self.get_trip(service_id=service_id)

        return context

    def form_valid(self, form):
        seats = form.cleaned_data.get("seats")
        session = self.request.session

        connection_id = session.get("connection_id")
        service_id = session.get("service_id")

        obj = Prosys(connection_id=connection_id)
        prepare_sale = obj.prepare_sale(service_id=service_id, seats=seats)

        session["seats"] = seats
        session["guid"] = prepare_sale.get("guid")

        return super().form_valid(form)

    def get_trip(self, service_id):
        """
        Get the current seats availability for a trip from the API.
        """

        session = self.request.session
        session["service_id"] = service_id

        obj = Prosys(connection_id=session.get("connection_id"))

        trip = obj.get_service(service_id)
        trip["reserved"] = self.get_reserved(trip=trip)
        trip["disabled"] = self.get_disabled(trip=trip)

        return trip

    def get_reserved(self, trip):
        """
        Build a map of reserved (or seats that are not allowed to be selected)
        """

        # build full seat map
        all = [{"row": x, "col": y} for x in range(12) for y in range(5)]

        # seats given by the api, subtract one since seats.js is zero indexed
        active = [
            {"row": int(x.get("row")) - 1, "col": int(x.get("col")) - 1}
            for x in trip.get("seats")
        ]

        # mark rest as reserved
        reserved = [x for x in all if x not in active]

        return reserved

    def get_disabled(self, trip):
        """
        Mark the central passage of the vehicle (col:2) as reserved.
        """

        # seats from api which are not free
        unavailable = [
            {"row": int(x.get("row")) - 1, "col": int(x.get("col")) - 1}
            for x in trip.get("seats")
            if x.get("status") != "Free"
        ]

        # central passage of the vehicle
        passage = [{"row": x, "col": 2} for x in range(12)]
        disabled = unavailable + passage

        return disabled
