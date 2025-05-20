from http import HTTPStatus
from unittest import skip

from django.test import TestCase
from django.urls import resolve, reverse_lazy

from payments.views import PaymentFailView, PaymentPendingView, PaymentSuccessView


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
        self.assertNotContains(response, "Hi there! I should not be on this page.")

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
    def test_payment_success_view_sends_notification_to_operator_via_email(self):
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
        self.assertNotContains(response, "Hi there! I should not be on this page.")

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
        self.assertNotContains(response, "Hi there! I should not be on this page.")

    def test_payment_fail_view_only_accepts_get_request(self):
        response = self.client.post(self.url)  # try POST

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertTemplateNotUsed(response, self.template_name)
