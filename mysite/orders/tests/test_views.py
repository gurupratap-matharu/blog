from http import HTTPStatus
from unittest.mock import MagicMock, patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse

from orders.factories import OrderFactory
from orders.forms import OrderSearchForm
from orders.views import OrderSearchView


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
