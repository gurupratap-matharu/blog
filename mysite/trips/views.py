from django.views.generic import TemplateView


class TripListView(TemplateView):
    template_name = "trips/trip_list.html"


class SeatsView(TemplateView):
    template_name = "trips/seats.html"


class OrderView(TemplateView):
    template_name = "trips/order.html"


class PaymentView(TemplateView):
    template_name = "trips/payment.html"


class PaymentSuccessView(TemplateView):
    template_name = "trips/payment_success.html"
