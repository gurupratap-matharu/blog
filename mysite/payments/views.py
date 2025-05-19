import logging
import random
import uuid
from datetime import timedelta
from http import HTTPStatus

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

import mercadopago

from .models import WebhookMessage

logger = logging.getLogger(__name__)
mercado_pago = mercadopago.SDK(settings.MP_ACCESS_TOKEN)


class PaymentView(TemplateView):
    template_name = "payments/payment.html"


class PaymentSuccessView(TemplateView):
    template_name = "payments/payment_success.html"


class PaymentPendingView(TemplateView):
    template_name = "payments/payment_pending.html"


class PaymentFailView(TemplateView):
    template_name = "payments/payment_fail.html"
    session_keys = ("q", "connection_id", "guid")

    def dispatch(self, request, *args, **kwargs):
        """
        Verify that session is valid with all keys else redirect to home.
        """

        if not all(k in request.session for k in self.session_keys):
            messages.info(request, settings.SESSION_EXPIRED_MESSAGE)
            return redirect("/")

        return super().dispatch(request, *args, **kwargs)


class MercadoPagoView(TemplateView):
    template_name = "payments/mercado_pago.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mp_public_key"] = settings.MP_PUBLIC_KEY
        context["preference"] = self.get_preference()

        return context

    def get_preference(self):
        order_id = str(uuid.uuid4())
        unit_price = round(random.random() * 100, 2)
        uri = self.request.build_absolute_uri
        BASE_URI = "https://ventanita.com.ar"

        picture_url = uri(static("assets/img/logos/ventanita.avif"))

        success = BASE_URI + reverse_lazy("payments:mercado-pago-success")
        failure = BASE_URI + reverse_lazy("payments:fail")
        pending = BASE_URI + reverse_lazy("payments:pending")
        notification_url = BASE_URI + reverse_lazy("payments:mercado-pago-webhook")

        preference_data = {
            "items": [
                {
                    "id": order_id,
                    "title": "Pasajes de Micro",
                    "description": "Pasajes de Micro",  # <-- could be customized
                    "currency_id": "ARS",
                    "picture_url": picture_url,
                    "category_id": "tickets",
                    "quantity": 1,
                    "unit_price": unit_price,
                }
            ],
            "back_urls": {
                "success": success,
                "failure": failure,
                "pending": pending,
            },
            "auto_return": "approved",
            "notification_url": notification_url,
            "statement_descriptor": "Ventanita",
            "external_reference": order_id,
            "binary_mode": True,
        }

        preference = mercado_pago.preference().create(preference_data)

        logger.info("preference:%s" % preference)

        return preference["response"]


def mercadopago_success(request):
    """
    Parses the query parameters sent by mercado pago when a payment is succesful
    and routes to our PaymentSuccess endpoint. By itself this view does not render any template
    but is just an intermediate processing step.

    This is not a webhook of mercado pago. My understanding is that mercado pago is appending
    payment response as query params to the `success_url` via GET request.

    At the time of implementation I realise that it might not be safe to show mercado pago
    payment details right in the query parameters.

    An example of successful query params is like this...

    /payments/success/?
    collection_id=54650347595&
    collection_status=approved&
    payment_id=54650347595&
    status=approved&
    external_reference=7a231700-d000-47d0-848b-65ff914a9a3e&
    payment_type=account_money&
    merchant_order_id=7712864656&
    preference_id=1272408260-35ff1ef7-3eb8-4410-b219-4a98ef386ac0&
    site_id=MLA&
    processing_mode=aggregator&
    merchant_account_id=null
    """

    params = request.GET

    order_id = params.get("external_reference")
    status = params.get("status")
    payment_id = params.get("payment_id")

    logger.info("mercado pago:%s" % params)

    # Remove webhook messages more than 1 week old
    last_week = timezone.now() - timedelta(days=7)
    WebhookMessage.objects.filter(received_at__lte=last_week).delete()

    # Save webhook message to DB irrespective of status
    WebhookMessage.objects.create(
        provider=WebhookMessage.MERCADOPAGO,
        received_at=timezone.now(),
        payload=params,
    )

    if (status == "approved") and order_id and payment_id:
        logger.info("mercadopago payment successful...")
        # TODO:Confirm order here...
        return redirect(reverse_lazy("payments:success"))

    return redirect(reverse_lazy("payments:fail"))


@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    """
    Webhook to receive payment updates from mercado pago.

    Veer we currently have this as a placeholder view.
    Confirmation about payment is handled by mercadopago_success view.
    """

    logger.info("MP webhook query params:%s", request.GET)
    logger.info("mp webhook request body:%s", request.body)

    return HttpResponse(
        "Messge received okay.", content_type="text/plain", status=HTTPStatus.OK
    )
