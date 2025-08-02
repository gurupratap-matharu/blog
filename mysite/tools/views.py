import logging

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from trips.models import Stats

logger = logging.getLogger(__name__)


class ToolsIndexView(TemplateView):
    template_name = "tools/tools_index.html"


class PriceEstimateView(TemplateView):
    template_name = "tools/price_estimate.html"
    no_data_msg = _(
        "No encontramos datos entre este tramo. ¿Porque no probás uno otro?"
    )

    def post(self, request, *args, **kwargs):
        origin = request.POST.get("origin")
        destination = request.POST.get("destination")

        logger.info("origin:%s, destination:%s" % (origin, destination))

        try:
            stats = Stats.objects.get(
                origin__slug=origin, destination__slug=destination
            )

        except Stats.DoesNotExist:
            messages.info(request, self.no_data_msg)
            stats = None

        context = super().get_context_data(**kwargs)
        context["stats"] = stats

        return self.render_to_response(context)
