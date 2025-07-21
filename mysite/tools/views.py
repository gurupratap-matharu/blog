from django.views.generic import TemplateView


class PriceEstimateView(TemplateView):
    template_name = "tools/price_estimate.html"
