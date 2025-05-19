from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _


class WebhookMessage(models.Model):
    """
    Generic table to store webhook json response in the DB
    """

    MERCADOPAGO = "MP"
    STRIPE = "SP"
    PAYWAY = "PW"
    MODO = "MO"
    OTHER = "OT"
    PROVIDER_CHOICES = [
        (MERCADOPAGO, "Mercado Pago"),
        (MODO, "Modo"),
        (PAYWAY, "Payway"),
        (STRIPE, "Stripe"),
        (OTHER, "Other"),
    ]

    provider = models.CharField(
        _("provider"), max_length=2, choices=PROVIDER_CHOICES, default=MERCADOPAGO
    )
    received_at = models.DateTimeField(help_text=_("When we received the message"))
    payload = models.JSONField(_("payload"), default=dict, encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = _("webhook message")
        verbose_name_plural = _("webhook messages")
        indexes = [
            models.Index(fields=["received_at"]),
        ]

    def __str__(self):
        return f"{self.get_provider_display()}:{self.received_at}"
