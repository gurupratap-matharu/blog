import logging

from django.conf import settings
from django.contrib import messages
from django.forms import formset_factory
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from trips.providers.prosys import Prosys

from .forms import OrderForm, PassengerForm

logger = logging.getLogger(__name__)


class OrderCreateView(FormView):
    template_name = "orders/order_form.html"
    form_class = OrderForm
    success_url = reverse_lazy("trips:payment")  # change this
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
        """Prepopulate the order form with logged user data if available"""

        initial = dict()
        user = self.request.user

        if user:
            initial["name"] = user.first_name
            initial["email"] = user.email
            initial["confirm_email"] = user.email

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = self._get_formset()
        return context

    def _get_formset(self):
        """
        Build the passenger formset
        """

        data = self.request.POST or None
        q = self.request.session.get("q")
        extra = int(q.get("num_of_passengers", 0))

        PassengerFormset = formset_factory(PassengerForm, extra=extra)
        formset = PassengerFormset(data=data)

        return formset

    def form_valid(self, form):
        """
        Here form obj is our order form which is already validated at this point.
        Now we need to validate the passenger formset and route to payment or route back with errors.
        """

        logger.info("order form is valid...")
        logger.info("cleaned data:%s" % form.cleaned_data)

        formset = self._get_formset()

        if not formset.is_valid():
            return super().form_invalid(form)

        logger.info("passenger formset is valid...")
        logger.info("formset cleaned data:%s" % formset.cleaned_data)

        price = self.get_price(passengers=formset)

        return super().form_valid(form)

    def get_price(self, passengers):
        session = self.request.session
        seats = session.get("seats")
        service_id = session.get("service_id")
        connection_id = session.get("connection_id")

        obj = Prosys(connection_id=connection_id)
        price = obj.get_price(service_id, passengers, seats)

        logger.info("price:%s" % price)

        return price
