import string

import factory
from faker import Faker
from trips.models import Location

fake = Faker()


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
