from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.text import slugify

from trips.factories import LocationFactory, StatsFactory
from trips.models import Location, Stats


class LocationModelTests(TestCase):
    """
    Test suite for the location model.
    """

    def test_str_representation(self):
        location = LocationFactory()
        self.assertEqual(str(location), f"{location.name}")

    def test_verbose_names(self):
        location = LocationFactory()

        self.assertEqual(str(location._meta.verbose_name), "location")
        self.assertEqual(str(location._meta.verbose_name_plural), "locations")

    def test_location_model_creation_is_accurate(self):
        location = LocationFactory()

        loc_db = Location.objects.first()

        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(loc_db.name, location.name)
        self.assertEqual(loc_db.slug, location.slug)
        self.assertEqual(loc_db.abbr, location.abbr)
        self.assertEqual(loc_db.city, location.city)
        self.assertEqual(loc_db.state, location.state)
        self.assertEqual(loc_db.postal_code, location.postal_code)
        self.assertEqual(loc_db.country, location.country)

    def test_location_slug_is_auto_generated(self):
        location = LocationFactory(slug=None)

        self.assertIsNotNone(location.slug)
        self.assertEqual(location.slug, slugify(location.name))


class StatsModelTests(TestCase):
    """
    Test suite for the stats model.
    """

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.origin = LocationFactory()
        cls.destination = LocationFactory()

    def test_str_representation(self):
        stats = StatsFactory(origin=self.origin, destination=self.destination)

        self.assertEqual(str(stats), f"{stats.origin}:{stats.destination}")

    def test_verbose_names(self):
        stats = StatsFactory(origin=self.origin, destination=self.destination)

        self.assertEqual(str(stats._meta.verbose_name), "stats")
        self.assertEqual(str(stats._meta.verbose_name_plural), "stats")

    def test_stats_model_creation_is_accurate(self):

        stats = StatsFactory(origin=self.origin, destination=self.destination)
        s_db = Stats.objects.first()

        self.assertEqual(Stats.objects.count(), 1)

        self.assertEqual(s_db.first_departure, stats.first_departure)
        self.assertEqual(s_db.last_departure, stats.last_departure)
        self.assertEqual(s_db.duration, stats.duration)
        self.assertEqual(s_db.price_economy, stats.price_economy)
        self.assertEqual(s_db.price_avg, stats.price_avg)
        self.assertEqual(s_db.num_departures, stats.num_departures)
        self.assertEqual(s_db.companies, stats.companies)

    def test_stats_cannot_have_same_origin_destination(self):
        loc = LocationFactory(name="Ushuaia")

        with self.assertRaises(ValidationError):
            StatsFactory(origin=loc, destination=loc).full_clean()
