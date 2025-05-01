import logging

from django.views.generic import TemplateView

from trips.providers.prosys import Prosys

logger = logging.getLogger(__name__)


class TripSearchView(TemplateView):
    template_name = "trips/trip_list.html"

    def get(self, request, *args, **kwargs):
        q = request.GET
        request.session["q"] = q
        self.origin, self.destination, self.departure = (
            q["origin"],
            q["destination"],
            q["departure"],
        )
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


class SeatsView(TemplateView):
    template_name = "trips/seats.html"


class OrderView(TemplateView):
    template_name = "trips/order.html"


class PaymentView(TemplateView):
    template_name = "trips/payment.html"


class PaymentSuccessView(TemplateView):
    template_name = "trips/payment_success.html"
