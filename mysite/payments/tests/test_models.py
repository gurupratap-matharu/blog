import uuid

from django.test import TestCase
from django.utils import timezone

from payments.models import WebhookMessage


class WebhookMessageTests(TestCase):
    def setUp(self):

        self.payload = {
            "collection_id": 54650347595,
            "collection_status": "approved",
            "payment_id": 54650347595,
            "status": "approved",
            "external_reference": str(uuid.uuid4()),
            "payment_type": "account_money",
            "merchant_order_id": "7712864656",
            "preference_id": str(uuid.uuid4()),
            "site_id": "MLA",
            "processing_mode": "aggregator",
        }

        self.obj = WebhookMessage.objects.create(
            provider=WebhookMessage.MERCADOPAGO,
            received_at=timezone.now(),
            payload=self.payload,
        )

    def test_str_representation(self):
        obj = WebhookMessage.objects.first()
        self.assertEqual(str(obj), f"{obj.get_provider_display()}:{obj.received_at}")

    def test_verbose_names(self):
        obj = WebhookMessage.objects.first()
        self.assertEqual(str(obj._meta.verbose_name), "webhook message")
        self.assertEqual(str(obj._meta.verbose_name_plural), "webhook messages")

    def test_obj_creation_is_correct(self):
        obj = WebhookMessage.objects.first()
        self.assertEqual(obj.payload, self.payload)
        self.assertEqual(obj.provider, WebhookMessage.MERCADOPAGO)
