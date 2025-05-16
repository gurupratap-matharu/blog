from datetime import datetime, timedelta
from unittest import skip

from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import SimpleTestCase, TestCase

from trips.forms import SeatForm, TripSearchForm


class TripSearchFormTests(TestCase):
    """
    Test suite to validate the home page search form.
    """

    @skip("VEER PLEASE IMPLEMENT ME")
    def test_invalid_origin_raises_exception(self):
        today = datetime.today()
        tomorrow = (today + timedelta(days=1)).strftime("%d-%m-%Y")

        data = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["123"],  # <- invalid origin
            "destination": ["MZA"],
            "departure": [tomorrow],
            "return": [""],
        }

        form = TripSearchForm(data=data)

        with self.assertRaises(Http404):
            form.validate()

    @skip("VEER PLEASE IMPLEMENT ME")
    def test_invalid_destination_raises_exception(self):
        today = datetime.today()
        tomorrow = (today + timedelta(days=1)).strftime("%d-%m-%Y")

        data = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["BUE"],
            "destination": ["123"],  # <- invalid destination
            "departure": [tomorrow],
            "return": [""],
        }

        form = TripSearchForm(data=data)

        with self.assertRaises(Http404):
            form.validate()

    def test_missing_origin_or_destination_raises_exception(self):
        today = datetime.today()
        tomorrow = (today + timedelta(days=1)).strftime("%d-%m-%Y")

        data_without_origin = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": [""],
            "destination": ["MZA"],
            "departure": [tomorrow],
            "return": [""],
        }

        data_without_destination = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["BUE"],
            "destination": [""],
            "departure": [tomorrow],
            "return": [""],
        }

        form_1 = TripSearchForm(data=data_without_origin)
        form_2 = TripSearchForm(data=data_without_destination)

        with self.assertRaises(ValidationError):
            form_1.validate()

        with self.assertRaises(ValidationError):
            form_2.validate()

    def test_invalid_departure_date_raises_exception(self):
        """
        Departure date is in the past and this should raise an exception.
        """

        today = datetime.today()
        yesterday = (today - timedelta(days=1)).strftime("%d-%m-%Y")

        data = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["BUE"],
            "destination": ["MZA"],
            "departure": [yesterday],
            "return": [""],
        }

        form = TripSearchForm(data=data)

        with self.assertRaises(ValidationError):
            form.validate()

    def test_missing_departure_date_raises_exception(self):
        """
        Departure date is missing and this should raise an exception.
        """

        data = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["BUE"],
            "destination": ["MZA"],
            "departure": [""],  # invalid departure date
            "return": [""],
        }

        form = TripSearchForm(data=data)

        with self.assertRaises(ValidationError):
            form.validate()

    def test_invalid_return_date_raises_exception(self):
        """
        Return date is before the departure date. This should raise an exception
        """
        today = datetime.today()
        tomorrow = (today + timedelta(days=1)).strftime("%d-%m-%Y")
        yesterday = (today - timedelta(days=1)).strftime("%d-%m-%Y")

        data = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["Buenos Aires"],
            "destination": ["Mendoza"],
            "departure": [tomorrow],
            "return": [yesterday],  # earlier than departure
        }

        form = TripSearchForm(data=data)

        with self.assertRaises(ValidationError):
            form.validate()

    def test_valid_form_with_return_date(self):
        """
        No exception should be raised and the test should just pass
        So nothing to assert here.
        """

        today = datetime.today()
        departure = today.strftime("%d-%m-%Y")
        return_date = (today + timedelta(days=1)).strftime("%d-%m-%Y")

        data = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["Buenos Aires"],
            "destination": ["Mendoza"],
            "departure": [departure],
            "return": [return_date],
        }

        form = TripSearchForm(data=data)
        form.validate()

    def test_valid_form_without_return_date(self):
        """
        No exception should be raised and the test should just pass
        So nothing to assert here.
        """

        today = datetime.today()
        departure = today.strftime("%d-%m-%Y")

        data = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["1"],
            "origin": ["Buenos Aires"],
            "destination": ["Mendoza"],
            "departure": [departure],
            "return": [""],
        }

        form = TripSearchForm(data=data)
        form.validate()

    def test_invalid_num_of_passengers_raises_exception(self):
        today = datetime.today().strftime("%d-%m-%Y")

        data_1 = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["11"],  # <- invalid number as > 10
            "origin": ["Buenos Aires"],
            "destination": ["Mendoza"],
            "departure": [today],
            "return": [""],
        }

        data_2 = {
            "trip_type": ["round_trip"],
            "num_of_passengers": ["0"],  # <- invalid number
            "origin": ["Buenos Aires"],
            "destination": ["Mendoza"],
            "departure": [today],
            "return": [""],
        }

        form_1 = TripSearchForm(data=data_1)
        form_2 = TripSearchForm(data=data_2)

        with self.assertRaises(ValidationError):
            form_1.validate()

        with self.assertRaises(ValidationError):
            form_2.validate()

    def test_invalid_trip_type_raises_exception(self):
        today = datetime.today().strftime("%d-%m-%Y")

        data_1 = {
            "trip_type": ["solo"],  # <- invalid string
            "num_of_passengers": ["1"],
            "origin": ["Buenos Aires"],
            "destination": ["Mendoza"],
            "departure": [today],
            "return": [""],
        }

        data_2 = {
            "trip_type": [""],  # <- missing trip type
            "num_of_passengers": ["1"],
            "origin": ["Buenos Aires"],
            "destination": ["Mendoza"],
            "departure": [today],
            "return": [""],
        }

        form_1 = TripSearchForm(data=data_1)
        form_2 = TripSearchForm(data=data_2)

        with self.assertRaises(ValidationError):
            form_1.validate()

        with self.assertRaises(ValidationError):
            form_2.validate()


class SeatFormTests(SimpleTestCase):
    def test_seat_form_is_valid_for_valid_data(self):
        data = {"seats": "11, 12"}
        expected = {"seats": ["11", "12"]}
        form = SeatForm(data=data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, expected)

    def test_seat_form_with_single_seat(self):
        actual = {"seats": "1"}
        expected = {"seats": ["1"]}

        form = SeatForm(data=actual)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, expected)

    def test_seat_form_cleans_up_spaces_in_data(self):
        data = {"seats": " 3,  5,  9   "}
        expected = {"seats": ["3", "5", "9"]}

        form = SeatForm(data=data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, expected)

    def test_seat_form_is_invalid_form_empty_data(self):
        form = SeatForm(data={"seats": ""})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.cleaned_data, {})
