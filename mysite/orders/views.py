from django.views.generic import TemplateView


class OrderCreateView(TemplateView):
    template_name = "orders/order_form.html"
