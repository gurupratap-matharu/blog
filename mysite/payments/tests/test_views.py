from datetime import timedelta
from http import HTTPStatus

from django.conf import settings
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse_lazy
from django.utils import timezone

from payments.views import PaymentFailView


class PaymentFailTests(TestCase):
    url = reverse_lazy("payments:fail")
    home_url = "/"
    template_name = "payments/payment_fail.html"

    def setUp(self) -> None:
        """
        Build the session for each test.
        """
        tomorrow = timezone.now() + timedelta(days=1)
        departure = tomorrow.strftime("%d-%m-%Y")

        self.q = {
            "trip_type": "one_way",
            "num_of_passengers": "2",
            "origin": "BUE",
            "destination": "MZA",
            "departure": departure,
            "return": "",
        }
        session = self.client.session
        session["q"] = self.q
        session["connection_id"] = "54321"
        session.save()

    def test_payment_fail_url_resolves_correct_view(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func.view_class, PaymentFailView)

    def test_payment_fail_redirects_to_home_for_invalid_session(self):
        # Arrange: we clear the session that's built in the setup() method
        # and verify it.

        self.client.session.pop("q")
        self.client.session.pop("connection_id")
        self.client.session.save()

        self.assertNotIn("q", self.client.session)
        self.assertNotIn("connection_id", self.client.session)
        self.assertNotIn("guid", self.client.session)

        # Act: hit the view via get
        response = self.client.get(self.url)

        # Assert: that we are redirected to home with a nice message
        self.assertRedirects(response, self.home_url, HTTPStatus.FOUND)
        self.assertTemplateNotUsed(response, self.template_name)

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(settings.SESSION_EXPIRED_MESSAGE, str(messages[0]))

    def test_payment_fail_html_content(self):
        self.fail()

    def test_payment_fail_works(self):
        self.fail()
