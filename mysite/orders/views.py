import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.forms import modelformset_factory
from django.http import FileResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, FormView, View

from trips.providers.prosys import Prosys

from .forms import OrderForm, OrderSearchForm, PassengerForm
from .models import Order, Passenger
from .renderers import Render

logger = logging.getLogger(__name__)


class OrderCreateView(CreateView):
    template_name = "orders/order_form.html"
    form_class = OrderForm
    success_url = reverse_lazy("payments:home")
    session_keys = ("q", "connection_id", "seats", "service_id")

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

        logger.info("data:%s" % data)

        return formset

    def form_valid(self, form):
        """
        Here form represent Order model which is validated at this point.
        formset represents Passenger Model.

        We need to
            - validate passenger formset, save it if valid else redirect
            - build order-passenger m2m relationship
            - store order data in session
            - call prepare_sale() to get guid
            - call get_price() to get price per seat
        """

        logger.info("order form is valid...")
        logger.info("cleaned data:%s" % form.cleaned_data)

        session = self.request.session
        service_id = session.get("service_id")
        seats = session.get("seats")

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

        obj = Prosys(connection_id=session.get("connection_id"))
        prepare_sale = obj.prepare_sale(service_id, seats)
        price = obj.get_price(service_id, seats)

        session["guid"] = prepare_sale["guid"]
        session["amount"] = price["payments"][0]["amount"]
        session["prepare_sale"] = prepare_sale
        session["price"] = price

        session["order_id"] = str(order.id)
        session["passengers"] = self.prepare_passengers(passengers, price)

        return super().form_valid(form)

    def prepare_passengers(self, passengers, price):
        """
        Prepare a compiled list of passengers with seats to store
        in session. This is needed by the webhook to confirm the sale.
        """

        seats = price.get("seats")
        passengers = [p.to_dict() for p in passengers]

        for passenger, seat in zip(passengers, seats):
            passenger["label"] = seat["seat"]
            passenger["service_id"] = seat["service"]
            passenger["amount"] = seat["amount"]

        return passengers


class OrderSearchView(FormView):
    form_class = OrderSearchForm
    failure_message = _("No pudimos encontrar sus pasajes.")
    template_name = "orders/order_search.html"
    order = None

    def form_valid(self, form):
        cd = form.cleaned_data

        try:
            self.order = Order.objects.get(
                email__iexact=cd["email"],
                reservation_code__iexact=cd["reservation_code"],
            )

        except Order.DoesNotExist as e:
            logger.warn(e)
            messages.warning(self.request, self.failure_message)

            return super().form_invalid(form)

        logger.info("order:%s" % self.order)

        return super().form_valid(form)

    def get_success_url(self):
        return self.order.get_cancel_url()


class OrderCancelView(DetailView):
    model = Order
    pk_url_kwarg = "id"
    template_name = "orders/order_cancel.html"
    success_msg = _("Hemos recibimos su solicitud exitosamente.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tickets"] = self.get_tickets()

        return context

    def get_tickets(self):
        session = self.request.session
        order = self.object

        obj = Prosys(connection_id=session.get("connection_id"))
        tickets = obj.get_tickets(guid=order.transaction_id)

        return tickets

    def post(self, request, *args, **kwargs):
        ticket_ids = request.POST.getlist("ticket_id")
        connection_id = request.session.get("connection_id")

        logger.info("ticket_ids:%s" % ticket_ids)

        obj = Prosys(connection_id=connection_id)

        data = []

        for ticket_id in ticket_ids:

            ticket = obj.check_ticket(ticket_id)
            retention_pct = ticket.get("details")["retention_pct"]

            refund = obj.refund(ticket_id=ticket_id, retention_pct=retention_pct)
            data.append(refund)

        self.send_cancellation_mail(ticket_ids, data)
        messages.success(request, self.success_msg)

        return redirect("/")

    def send_cancellation_mail(self, ticket_ids, data):
        """
        Send order cancellation confirmation to the user and
        a copy to us.
        """

        logger.info("sending order cancel email...")

        order = self.get_object()
        json_response = json.dumps(data, ensure_ascii=False, indent=4)

        context = dict()
        context["order"] = order
        context["data"] = data
        context["ticket_ids"] = ticket_ids

        subject_path = "orders/emails/order_cancel_subject.txt"
        message_path = "orders/emails/order_cancel_message.txt"

        subject = render_to_string(subject_path, context).strip()
        message = render_to_string(message_path, context).strip()

        user_email = EmailMultiAlternatives(
            subject,
            message,
            settings.NOTIFICATION_EMAIL,
            [order.email],
            cc=[settings.CANCELLATION_EMAIL],
            reply_to=[settings.CANCELLATION_EMAIL],
        )

        admin_message = (
            f"Name             :{order.name}\n"
            f"Phone            :{order.phone_number}\n"
            f"Reservation Code :{order.reservation_code}\n"
            f"Transaction Id   :{order.transaction_id}\n"
            f"Email            :{order.email}\n"
            f"Ticket Ids       :{ticket_ids}\n"
            f"API Response     :{json_response}\n"
        )

        admin_email = EmailMultiAlternatives(
            subject,
            admin_message,
            settings.NOTIFICATION_EMAIL,
            [settings.CANCELLATION_EMAIL],
        )

        mails_sent = user_email.send()
        admin_email.send()

        return mails_sent


class TicketsView(View):
    def get(self, request, *args, **kwargs):
        pdf = Render().get_ticket_pdf()

        return FileResponse(pdf, as_attachment=False, filename="tickets.pdf")
