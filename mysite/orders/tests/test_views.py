from http import HTTPStatus
from unittest.mock import MagicMock, patch

from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse

from orders.factories import OrderFactory
from orders.forms import OrderSearchForm
from orders.views import OrderCancelView, OrderSearchView
from trips.providers.factories import ProsysFactory


class OrderSearchTests(TestCase):
    """
    Test suite for the order search view.
    """

    url = reverse("orders:order-search")
    template_name = "orders/order_search.html"

    def test_view_resolves_correct_url(self):
        resolver_match = resolve(self.url)
        self.assertEqual(resolver_match.func.view_class, OrderSearchView)

    def test_order_search_works_via_get(self):
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Devolución de pasajes")
        self.assertNotContains(response, "Hi I should not be on this page")
        self.assertIsInstance(response.context["form"], OrderSearchForm)

    def test_invalid_order_post_shows_message(self):
        # Arrange: Create an order which does not exists
        data = {
            "reservation_code": "ABC123",  # some random code
            "email": "passenger@email.com",
        }

        # Act
        response = self.client.post(self.url, data=data)

        # Assert
        # Make sure user is shown a valid message and stays on the same page
        # Make sure user is not redirected to order cancel view
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertTemplateNotUsed(response, "orders/order_cancel.html")
        self.assertEqual(len(messages), 1)
        self.assertEqual(OrderSearchView.failure_message, str(messages[0]))

    @patch("orders.views.Prosys")
    def test_order_search_is_case_insensitive(self, MockProsys):
        """
        Here a user searches for his/her valid order but enters the fields
        in different case.

        - Reservation_codes are all auto generated in Uppercase so let the user enter
          them in lowercase
        - Whereas email is generally lower case so let the user enter it in uppercase.

        """

        # Arrange: Patch prosys method & create a paid order
        MockProsys.get_tickets = MagicMock(return_value=dict())

        order = OrderFactory(paid=True)
        data = {
            "reservation_code": order.reservation_code.lower(),
            "email": order.email.upper(),
        }

        # Act
        response = self.client.post(self.url, data=data, follow=True)

        # Assert
        # Make sure order is found and user is redirected to order cancel page
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, order.get_cancel_url(), HTTPStatus.FOUND)
        self.assertTemplateNotUsed(response, self.template_name)
        self.assertTemplateUsed(response, "orders/order_cancel.html")
        self.assertEqual(len(messages), 0)

    @patch("orders.views.Prosys")
    def test_valid_future_order_is_found(self, MockProsys):
        """
        Incase of valid order search user is directed to OrderCancelView
        which calls the api to get the tickets.

        We patch that method and return an empty dict to just test that
        the user is redirected.
        """

        # Arrange
        # Patch prosys method
        MockProsys.get_tickets = MagicMock(return_value=dict())

        # Create a valid paid order in DB
        order = OrderFactory(paid=True)
        data = dict(reservation_code=order.reservation_code, email=order.email)

        # Act
        response = self.client.post(self.url, data=data, follow=True)

        # Assert
        # Make sure user is redirected to order cancel page
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, order.get_cancel_url(), HTTPStatus.FOUND)
        self.assertTemplateNotUsed(response, self.template_name)
        self.assertTemplateUsed(response, "orders/order_cancel.html")
        self.assertEqual(len(messages), 0)


class OrderCancelTests(TestCase):
    """
    Test suite for OrderCancelView.
    This is a Detail View for the Order model and has a simple form embedded in html directly.

    The view itself has a post method that hits the api to cancel an order.

    For testing both get() and post() we cannot hit the api so we'll mock or patch it in our
    tests for simplicity.
    """

    template_name = "orders/order_cancel.html"

    def test_view_resolves_correct_url(self):
        # Arrange
        order = OrderFactory(paid=True)
        url = order.get_cancel_url()

        # Act
        resolver_match = resolve(url)

        # Assert
        self.assertEqual(resolver_match.func.view_class, OrderCancelView)

    @patch("orders.views.Prosys")
    def test_order_cancel_works_via_get(self, MockProsys):
        # Arrange
        MockProsys.get_tickets = ProsysFactory().get_tickets
        order = OrderFactory(paid=True)

        # Act
        response = self.client.get(order.get_cancel_url())
        # Assert

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Devolución de pasajes")
        self.assertNotContains(response, "Hi I should not be on this page")
        self.assertContains(response, f"{order.name}")
        self.assertContains(response, "Devolver")

    @patch("orders.views.Prosys")
    def test_valid_post_cancels_order(self, MockProsys):
        """
        The entire Prosys class is a Magic Mock here available in the MockProsys
        variable.

        We need to instantiate it and further patch its refund method with expected
        behavior.
        """

        # Arrange
        order = OrderFactory(paid=True)
        ticket_ids = ["11", "12"]
        data = dict(ticket_id=ticket_ids)

        obj = MockProsys()
        obj.refund = MagicMock(return_value={"status": "ok"})

        # Act
        response = self.client.post(order.get_cancel_url(), data=data, follow=True)

        # Assert
        # Make sure user is redirected to Home with a valid confirmation message
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateNotUsed(response, "orders/order_cancel.html")
        self.assertRedirects(response, "/", HTTPStatus.FOUND)

        self.assertEqual(len(messages), 1)
        self.assertEqual(OrderCancelView.success_msg, str(messages[0]))

        # Make sure user receives an email confirmation
        # Make sure we receive an email with the cancellation details as well
        self.assertEqual(len(mail.outbox), 2)

    def test_invalid_post_displays_message(self):
        self.fail()

    def test_non_refundable_orders_are_disabled(self):
        self.fail()
