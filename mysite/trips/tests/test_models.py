from django.test import TestCase
from django.utils.text import slugify

from trips.factories import LocationFactory
from trips.models import Location


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
