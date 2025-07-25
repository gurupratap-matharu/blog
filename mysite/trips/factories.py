import random
import string
from datetime import timedelta

import factory
from factory import fuzzy
from faker import Faker
from trips.models import Location, Stats

fake = Faker()

companies = ["Andesmar", "Balut", "Chevallier", "20 De Junio", "Cata", "Dumascat"]


class LocationFactory(factory.django.DjangoModelFactory):
    """
    Factory to create fake locations for testing purposes
    """

    class Meta:
        model = Location
        django_get_or_create = ("name",)

    name = factory.Faker("city")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    abbr = factory.Faker("lexify", letters=string.ascii_uppercase)
    address_line1 = factory.Faker("address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    postal_code = factory.Faker("postalcode")
    country = factory.Faker("country_code")
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")


class StatsFactory(factory.django.DjangoModelFactory):
    """
    Factory to create fixtures of Statistics between to locations for testing
    purposes.
    """

    class Meta:
        model = Stats

    origin = factory.SubFactory(LocationFactory)
    destination = factory.SubFactory(LocationFactory)

    first_departure = factory.Faker("time_object")
    last_departure = factory.Faker("time_object")
    duration = factory.LazyAttribute(
        lambda o: timedelta(seconds=random.randrange(3600, 36000))
    )
    price_economy = fuzzy.FuzzyDecimal(10000, 80000, precision=0)
    price_avg = fuzzy.FuzzyDecimal(10000, 80000, precision=0)
    num_departures = fuzzy.FuzzyInteger(1, 20)
    companies = factory.LazyAttribute(
        lambda o: ", ".join(random.sample(companies, k=3))
    )
