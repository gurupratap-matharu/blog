import logging

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from trips.models import Stats


logger = logging.getLogger(__name__)


def tools_index(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "tools/tools_index.html", {})


def price_estimate(request: HttpRequest) -> HttpResponse:
    ctx = dict()
    if request.method == "POST":
        origin = request.POST.get("origin")
        destination = request.POST.get("destination")

        logger.info("origin:%s, destination:%s" % (origin, destination))

        try:
            stats = Stats.objects.get(
                origin__slug=origin, destination__slug=destination
            )

        except Stats.DoesNotExist:
            no_data_msg = _(
                "No encontramos datos entre este tramo. ¿Porque no probás uno otro?"
            )
            messages.info(request, no_data_msg)
            stats = None

        ctx["stats"] = stats

    return TemplateResponse(request, "tools/price_estimate.html", ctx)
