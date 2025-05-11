from django.test import TestCase
from django.urls import reverse_lazy


class TripSearchViewTests(TestCase):
    """
    Test suite for the the main TripSearchView which is triggered
    by search form on homepage.
    """

    template_name = "trips/trip_list.html"
    url = reverse_lazy("trips:trip-search")

    def test_trip_search_view_resolves_correct_url(self):
        pass
