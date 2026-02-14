import uuid
from datetime import timedelta
from http import HTTPStatus
from unittest import skip

from django.test import Client, TestCase
from django.urls import resolve, reverse_lazy
from django.utils import timezone

from payments.models import WebhookMessage
from payments.views import (
    PaymentFailView,
    PaymentPendingView,
    PaymentSuccessView,
    PaymentView,
    mercadopago_success,
    mercadopago_webhook,
)


class PaymentViewTests(TestCase):
    url = reverse_lazy("payments:home")
    home_url = "/"
    template_name = PaymentView.template_name

    def test_payment_view_url_resolves_correct_view(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func.view_class, PaymentView)

    def test_payment_view_works_correctly(self):
        response = self.client.get(self.url, headers={"accept-language": "es"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Pago")
        self.assertNotContains(
            response, "Hi there! I should not be on this page."
        )

    def test_payment_view_only_accepts_get_request(self):
        response = self.client.post(self.url)  # try POST

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertTemplateNotUsed(response, self.template_name)

    @skip
    def test_payment_view_redirects_home_for_invalid_session(self):
        self.fail()

    @skip
    def test_payment_view_works_for_valid_session(self):
        self.fail()


class PaymentSuccessTests(TestCase):
    url = reverse_lazy("payments:success")
    home_url = "/"
    template_name = PaymentSuccessView.template_name

    def test_payment_success_url_resolves_correct_view(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func.view_class, PaymentSuccessView)

    def test_payment_success_view_works_correctly(self):
        response = self.client.get(self.url, headers={"accept-language": "es"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Pago Éxitoso")
        self.assertContains(response, "¡Pasajes Confirmados!")
        self.assertContains(response, "Reservar otro pasaje")
        self.assertNotContains(
            response, "Hi there! I should not be on this page."
        )

    def test_payment_success_view_only_accepts_get_request(self):
        response = self.client.post(self.url)  # try POST

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertTemplateNotUsed(response, self.template_name)

    @skip
    def test_payment_success_view_ticket_pdf_download_link_works(self):
        self.fail()

    @skip
    def test_payment_success_view_add_to_calendar_link_works(self):
        self.fail()

    @skip
    def test_payment_success_view_sends_ticket_via_email_to_user(self):
        self.fail()

    @skip
    def test_payment_success_view_sends_notification_to_operator_via_email(
        self,
    ):
        self.fail()

    @skip
    def test_payment_success_clears_session(self):
        self.fail()


class PaymentPendingTests(TestCase):
    url = reverse_lazy("payments:pending")
    home_url = "/"
    template_name = PaymentPendingView.template_name

    def test_payment_pending_url_resolves_correct_view(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func.view_class, PaymentPendingView)

    def test_payment_pending_view_works_correctly(self):
        response = self.client.get(self.url, headers={"accept-language": "es"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Pago Pendiente")
        self.assertContains(response, "Ir al Home")
        self.assertNotContains(
            response, "Hi there! I should not be on this page."
        )

    def test_payment_pending_view_only_accepts_get_request(self):
        response = self.client.post(self.url)  # try POST

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertTemplateNotUsed(response, self.template_name)


class PaymentFailTests(TestCase):
    url = reverse_lazy("payments:fail")
    home_url = "/"
    template_name = PaymentFailView.template_name

    def test_payment_fail_url_resolves_correct_view(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func.view_class, PaymentFailView)

    def test_payment_fail_view_works_correctly(self):
        response = self.client.get(self.url, headers={"accept-language": "es"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Pago sin éxito")
        self.assertContains(response, "Ir al home")
        self.assertContains(response, "Probar de nuevo")
        self.assertNotContains(
            response, "Hi there! I should not be on this page."
        )

    def test_payment_fail_view_only_accepts_get_request(self):
        response = self.client.post(self.url)  # try POST

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertTemplateNotUsed(response, self.template_name)


class MercadoPagoSuccessTests(TestCase):
    """
    Test suite to check if mercado pago response is parsed and stored in the DB
    correctly.
    This is the view that redirects to payments success if payment is approved.
    We use this view as a `webhook` by parsing its query params.
    """

    url = reverse_lazy("payments:mercado-pago-success")
    order_id = str(uuid.uuid4())
    success_params = {
        "collection_id": "7654321",
        "collection_status": "approved",
        "payment_id": "7654321",
        "status": "approved",
        "external_reference": order_id,
    }
    failure_params = {
        "collection_id": "7654321",
        "collection_status": "rejected",
        "payment_id": "7654321",
        "status": "rejected",
        "external_reference": order_id,
    }

    def test_view_resolves_correct_url(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func, mercadopago_success)

    def test_redirects_to_payments_success_for_valid_payment(self):
        # Arrange: we have the success params already defined

        # Act: hit the view via get with follow=True to follow redirect...
        response = self.client.get(
            self.url, query_params=self.success_params, follow=True
        )
        # Assert: that we are redirected to success page
        self.assertRedirects(
            response, reverse_lazy("payments:success"), HTTPStatus.FOUND
        )
        self.assertTemplateUsed(response, PaymentSuccessView.template_name)

    def test_redirects_payments_fail_for_invalid_payment(self):
        response = self.client.get(
            self.url, query_params=self.failure_params, follow=True
        )

        # Assert: that we are redirected to payment fail page
        self.assertRedirects(
            response, reverse_lazy("payments:fail"), HTTPStatus.FOUND
        )
        self.assertTemplateUsed(response, PaymentFailView.template_name)

    def test_stores_query_params_in_webhook_message_model(self):
        # Arrange: we have the success params already defined
        # Check no webhook message in db
        self.assertEqual(WebhookMessage.objects.count(), 0)

        # Act: hit the view via get with follow=True to follow redirect...
        response = self.client.get(
            self.url, query_params=self.success_params, follow=True
        )
        # Assert: that we are redirected to success page
        self.assertRedirects(
            response, reverse_lazy("payments:success"), HTTPStatus.FOUND
        )
        self.assertTemplateUsed(response, PaymentSuccessView.template_name)

        # Assert: webhook message saved in DB
        wm = WebhookMessage.objects.first()
        self.assertEqual(WebhookMessage.objects.count(), 1)
        self.assertEqual(wm.payload, self.success_params)

    def test_deletes_webhooks_messages_older_than_a_week(self):
        # Arrange: we create a webhook message older than a week
        old_message = WebhookMessage.objects.create(
            provider=WebhookMessage.MERCADOPAGO,
            received_at=timezone.now() - timedelta(days=8),
            payload={"name": "veer"},
        )
        self.assertEqual(WebhookMessage.objects.count(), 1)

        # Act: hit the view via get with follow=True to follow redirect...
        response = self.client.get(
            self.url, query_params=self.success_params, follow=True
        )

        # Assert: We are redirected to success page
        self.assertRedirects(
            response, reverse_lazy("payments:success"), HTTPStatus.FOUND
        )
        self.assertTemplateUsed(response, PaymentSuccessView.template_name)

        # Assert: old webhook message is deleted
        self.assertEqual(WebhookMessage.objects.count(), 1)

        wm = WebhookMessage.objects.first()
        self.assertEqual(wm.payload, self.success_params)
        self.assertNotEqual(wm.payload, old_message.payload)


class MercadoPagoWebhookTests(TestCase):
    """
    Test suite to check the integrity of Mercado Pago webhook endpoint.
    Incomplete. Veer if you develop the view further please add tests here.
    """

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.url = reverse_lazy("payments:mercado-pago-webhook")

    def test_mercadopago_view_resolves_correct_url(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func, mercadopago_webhook)

    def test_webhook_does_not_accept_get_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
