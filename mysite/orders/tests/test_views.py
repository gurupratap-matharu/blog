import string
from datetime import timedelta
from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

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
        # Arrange
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Devolución de pasajes")
        self.assertNotContains(response, "Hi I should not be on this page")
        self.assertIsInstance(response.context["form"], OrderSearchForm)

    def test_invalid_order_post_shows_message(self):

        # Arrange
        reservation_code = get_random_string(
            length=6, allowed_chars=string.ascii_uppercase
        )
        three_days_from_now = timezone.now() + timedelta(days=3)
        travel_date = three_days_from_now.date().strftime("%d-%m-%Y")

        data = {
            "reservation_code": reservation_code,
            "travel_date": travel_date,
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

    def test_valid_past_order_is_not_found(self):
        self.fail("Currently we do not have a way to find if an order is past locally")

    def test_valid_future_order_is_found(self):
        # Arrange

        # 1. Create a valid paid order in DB
        order = OrderFactory().valid_order()

        # 2. Create data for post
        three_days_from_now = timezone.now() + timedelta(days=3)
        travel_date = three_days_from_now.date().strftime("%d-%m-%Y")
        data = {
            "reservation_code": order.reservation_code,
            "travel_date": travel_date,
            "email": order.email,
        }

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

    def test_user_with_multiple_future_orders_on_same_day(self):
        self.fail()
