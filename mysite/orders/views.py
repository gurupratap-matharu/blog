import logging

from django.conf import settings
from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import OrderForm, PassengerForm
from .models import Passenger

logger = logging.getLogger(__name__)


class OrderCreateView(CreateView):
    template_name = "orders/order_form.html"
    form_class = OrderForm
    success_url = reverse_lazy("payments:home")
    session_keys = ("q", "connection_id", "seats", "guid", "service_id")

    def dispatch(self, request, *args, **kwargs):
        """
        Verify that session is valid with all keys else redirect to home.
        """

        if not all(k in request.session for k in self.session_keys):
            messages.info(request, settings.SESSION_EXPIRED_MESSAGE)
            return redirect("/")

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Prepopulate the order form with loggedin user data"""

        if self.request.user.is_authenticated:
            user = self.request.user
            return {
                "name": user.first_name,
                "email": user.email,
                "confirm_email": user.email,
            }
        return {}

    def get_context_data(self, **kwargs):
        """Add passenger formset to context"""

        context = super().get_context_data(**kwargs)
        context["formset"] = self._get_formset()
        return context

    def _get_formset(self):
        """
        Build the passenger formset
        """

        q = self.request.session.get("q")
        extra = int(q.get("num_of_passengers", 0))
        data = self.request.POST or None
        queryset = Passenger.objects.none()

        PassengerFormset = modelformset_factory(
            model=Passenger, form=PassengerForm, extra=extra
        )
        formset = PassengerFormset(data=data, queryset=queryset)

        return formset

    def form_valid(self, form):
        """
        Here form represent Order model which is validated at this point.
        formset represents Passenger Model.

        We need to
            - validate passenger formset, save it if valid else redirect
            - build order-passenger m2m relationship
            - store order data in session
        """

        logger.info("order form is valid...")
        logger.info("cleaned data:%s" % form.cleaned_data)

        session = self.request.session
        formset = self._get_formset()

        if not formset.is_valid():
            return super().form_invalid(form)

        # Create passenger objects
        order = form.save()
        passengers = formset.save()

        # Create and save order -> passenger m2m
        order.passengers.add(*passengers)
        order.save()

        logger.info("passenger formset is valid...")
        logger.info("formset cleaned data:%s" % formset.cleaned_data)
        logger.info("passengers:%s" % passengers)

        # Save order.id, price in session so payments can access it
        session["order_id"] = str(order.id)
        session["passengers"] = self.prepare_passengers(passengers)

        return super().form_valid(form)

    def prepare_passengers(self, passengers):
        """
        Prepare a compiled list of passengers with seats to store
        in session. This is needed by the webhook to confirm the sale.
        """

        session = self.request.session
        price = session.get("price")
        seats = price.get("seats")

        passengers = [p.to_dict() for p in passengers]

        for passenger, seat in zip(passengers, seats):
            passenger["label"] = seat["seat"]
            passenger["service_id"] = seat["service"]
            passenger["amount"] = seat["amount"]

        return passengers
