import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from trips.forms import TripSearchForm
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


class SeatsView(TemplateView):
    template_name = "trips/seats.html"
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
        context["trip"] = self.get_seat_map(service_id=service_id)
        return context

    def post(self, request, *args, **kwargs):
        """
        Store seat numbers in session and redirect to order create.
        """
        session = request.session
        passengers = session["q"]["num_of_passengers"]
        seats = request.POST.getlist("seats")

        if len(seats) != int(passengers):
            messages.info(request, f"Elegí {passengers} asientos")
            return redirect(request.path_info)

        session["seats"] = seats

        return redirect(reverse_lazy("orders:order-create"))

    def get_seat_map(self, service_id):
        """
        Get the current seats availability for a trip from the API.
        """

        session = self.request.session
        session["service_id"] = service_id

        obj = Prosys(connection_id=session.get("connection_id"))

        trip = obj.get_service_with_seat_map(service_id)
        return trip


class SearchView(TemplateView):
    template_name = "trips/search.html"
