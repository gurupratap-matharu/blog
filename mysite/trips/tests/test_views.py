import uuid
from datetime import timedelta
from http import HTTPStatus
from unittest import skip
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone

from trips.views import SeatsView, TripDetailView, TripSearchView

from .utils import SEARCH_RESULTS, SERVICE, STOPS


class TripSearchViewTests(TestCase):
    """
    Test suite for the the main TripSearchView which is triggered
    by search form on homepage.
    """

    template_name = "trips/trip_list.html"
    url = reverse_lazy("trips:trip-search")
    search_results = SEARCH_RESULTS

    query_params = {
        "trip_type": "one_way",
        "num_of_passengers": 1,
        "origin": "GYU",
        "destination": "BUE",
        "departure": "16-05-2025",
        "return": "",
        "company": "",
    }

    @patch("trips.views.Prosys")
    def test_trip_search_view_resolves_correct_url(self, MockProsys):
        # Arrange: mock the search() method get a dummy results

        obj = MockProsys()
        obj.search = MagicMock(return_value=self.search_results)

        # Act
        response = self.client.get(self.url, query_params=self.query_params)

        # Assert
        self.assertIs(response.resolver_match.func.view_class, TripSearchView)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "")
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_trip_search_redirects_for_bad_query(self):
        self.fail()

    def test_trip_search_stores_query_in_session(self):
        self.fail()

    def test_trip_search_view_context(self):
        self.fail()

    def test_trip_search_view_search_method(self):
        self.fail()

    def test_trip_search_works_for_valid_query(self):
        self.fail()


class TripDetailViewTests(TestCase):
    """
    Test suite for trip detail view that shows stops for a certain trip.
    """

    template_name = "trips/trip_detail.html"
    url = reverse_lazy("trips:trip-detail", kwargs={"service_id": 1})
    home_url = "/"
    stops = STOPS

    def setUp(self) -> None:
        """
        We need to build the session for each test.
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

    @patch("trips.views.Prosys")
    def test_trip_detail_url_resolves_correct_view(self, MockProsys):
        # Arrange: mock the get_route() method get a dummy service

        obj = MockProsys()
        obj.get_route = MagicMock(return_value=self.stops)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertIs(response.resolver_match.func.view_class, TripDetailView)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Paradas")
        self.assertNotContains(response, "Hi I should not be on this page")

    @patch("trips.views.Prosys")
    def test_trip_detail_view_works(self, MockProsys):
        # Arrange: mock the get_route() method get a dummy service

        obj = MockProsys()
        obj.get_route = MagicMock(return_value=self.stops)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn("route", response.context)
        self.assertEqual(response.context["route"], self.stops)

    def test_trip_detail_view_redirects_to_home_incase_of_invalid_session(self):
        # Arrange: remove search query from session on purpose
        session = self.client.session
        session.pop("q")
        session.save()

        self.assertNotIn("q", self.client.session)
        self.assertNotIn("q", session)

        # Act: hit the view via get and with an invalid session
        response = self.client.get(self.url)

        # Assert: that we are redirected to home with a nice message
        self.assertRedirects(response, self.home_url, HTTPStatus.FOUND)
        self.assertTemplateNotUsed(response, self.template_name)

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(settings.SESSION_EXPIRED_MESSAGE, str(messages[0]))


class SeatViewTests(TestCase):
    """
    Test suite for seat view.

    Remember veer in this test we patch the Prosys client where it is `called`
    i.e. 'trips.views.Prosys' and not where it is `defined`
    i.e. in 'trips.providers.prosys.Prosys'
    """

    template_name = "trips/seats.html"
    url = reverse_lazy("trips:seats", kwargs={"service_id": 1})
    order_url = reverse_lazy("orders:order-create")
    home_url = "/"
    service = SERVICE

    def setUp(self) -> None:
        """
        We need to build the session for each test.
        """

        tomorrow = timezone.now() + timedelta(days=1)
        departure = tomorrow.strftime("%d-%m-%Y")

        # user searched for this
        self.q = {
            "trip_type": "one_way",
            "num_of_passengers": "2",
            "origin": "BUE",
            "destination": "MZA",
            "departure": departure,
            "return": "",
        }
        self.connection_id = "54321"

        # user selected this trip
        self.service_id = "2"

        session = self.client.session
        session["q"] = self.q
        session["connection_id"] = self.connection_id
        session["service_id"] = self.service_id
        session.save()

    @skip("Veer please figure out how to write this one!")
    @patch("trips.views.Prosys")
    def test_get_seat_map_method(self, MockProsys):
        # Arrange: mock the api call
        obj = MockProsys()
        obj.get_service_with_seat_map = MagicMock(return_value=self.service)

        # Act
        # TODO: Veer i don't know how to call the view method with a request

    @patch("trips.views.Prosys")
    def test_seat_view_works_via_get(self, MockProsys):
        # Arrange: mock the get_service_with_seat_map() method get a dummy seatmap

        obj = MockProsys()
        obj.get_service_with_seat_map = MagicMock(return_value=self.service)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertIs(response.resolver_match.func.view_class, SeatsView)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Elegir Asiento")
        self.assertIn("trip", response.context)
        self.assertNotContains(response, "Hi I should not be on this page")

        obj.get_service_with_seat_map.assert_called_with(service_id=self.service_id)

    def test_redirects_home_incase_of_invalid_selection(self):
        """
        Test that a valid message is show incase user selects seats not equal
        to the number of passengers in initial query.
        """

        # Arrange: in setup we have passengers here we select three seats which are invalid
        passengers = self.q.get("num_of_passengers")
        data = {"seats": ["1", "2", "3"]}
        # Act
        response = self.client.post(self.url, data=data)

        # Assert
        self.assertRedirects(response, self.url, HTTPStatus.FOUND)

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(f"Elegí {passengers} asientos", str(messages[0]))

    @skip("Veer please implement me")
    def test_seat_view_reserved_seats(self):
        self.fail()

    def test_seat_view_redirects_to_home_incase_of_invalid_session(self):
        # Arrange: remove search query from session on purpose
        session = self.client.session
        session.pop("q")
        session.save()

        self.assertNotIn("q", self.client.session)
        self.assertNotIn("q", session)

        # Act: hit the view via get and with an invalid session
        response = self.client.get(self.url)

        # Assert: that we are redirected to home with a nice message
        self.assertRedirects(response, self.home_url, HTTPStatus.FOUND)
        self.assertTemplateNotUsed(response, self.template_name)

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(settings.SESSION_EXPIRED_MESSAGE, str(messages[0]))

    @patch("trips.views.Prosys")
    def test_seat_view_sets_service_id_in_session_on_valid_post(self, MockProsys):
        # Arrange: mock the get_service_with_seat_map() to get a dummy seatmap
        # also verify that session does not contain `service_id`

        obj = MockProsys()
        obj.get_service_with_seat_map = MagicMock(return_value=self.service)

        self.assertNotIn("service_id", self.client.session)

        # Act: hit the view via get
        response = self.client.get(self.url, follow=True)

        # Assert: service_id is present is session now
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("service_id", self.client.session)
        self.assertEqual(self.client.session["service_id"], 1)

    @patch("trips.views.Prosys")
    def test_seat_view_works_on_valid_post(self, MockProsys):
        """
        On valid post the seat view calls the `prepare_sale` method on prosys
        We'll mock it with a demo response.
        """

        # Arrange
        guid = str(uuid.uuid4())
        data = {"seats": "11, 12"}

        obj = MockProsys()
        obj.prepare_sale = MagicMock(return_value={"guid": guid})
        obj.get_service = MagicMock(return_value=self.service)

        # Act: hit the view via get so that service_id is set in session
        response = self.client.get(self.url, follow=True)

        # Act: post will redirect to order-create so make `follow=True`
        response = self.client.post(path=self.url, data=data, follow=True)

        # Assert: verify redirection
        self.assertRedirects(
            response=response,
            expected_url=self.order_url,
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

        # Verify content of final redirected page
        self.assertTemplateUsed(response, "orders/order_form.html")
        self.assertNotContains(response, "Hi I should not be on this page!")

        # Verify session values
        self.assertEqual(self.client.session["seats"], ["11", "12"])
        self.assertEqual(self.client.session["guid"], guid)
