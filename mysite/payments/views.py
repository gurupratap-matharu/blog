from django.views.generic import TemplateView


class PaymentView(TemplateView):
    template_name = "payments/payment.html"


class PaymentSuccessView(TemplateView):
    template_name = "payments/payment_success.html"


class PaymentFailView(TemplateView):
    template_name = "payments/payment_fail.html"


# Create your views here.
