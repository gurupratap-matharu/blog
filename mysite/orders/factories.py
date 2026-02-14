import string

from django.utils.crypto import get_random_string

import factory
from factory import fuzzy
from faker import Faker

from orders.models import Order, Passenger


fake = Faker()


class OrderFactory(factory.django.DjangoModelFactory):
    """
    Factory to create fake orders in the system.
    """

    class Meta:
        model = Order

    name = factory.Faker("name_nonbinary")
    email = factory.LazyAttribute(
        lambda obj: "%s@example.com" % obj.name.replace(" ", "-").lower()
    )
    phone_number = factory.LazyAttribute(
        lambda _: (fake.country_calling_code() + fake.phone_number())[:14]
    )
    paid = factory.Faker("boolean")
    payment_id = factory.LazyAttribute(
        lambda obj: fake.bban() if obj.paid else ""
    )
    transaction_id = factory.LazyAttribute(
        lambda obj: fake.uuid4() if obj.paid else ""
    )
    reservation_code = factory.LazyAttribute(
        lambda obj: (
            get_random_string(length=6, allowed_chars=string.ascii_uppercase)
            if obj.paid
            else ""
        )
    )


class PassengerFactory(factory.django.DjangoModelFactory):
    """
    Factory to create fake passengers for testing purpose.
    """

    class Meta:
        model = Passenger
        django_get_or_create = ("first_name",)

    document_type = fuzzy.FuzzyChoice(
        Passenger.DOCUMENT_TYPE_CHOICES, getter=lambda c: c[0]
    )
    document_number = factory.Faker("ssn")
    nationality = factory.Faker("country_code")
    first_name = factory.Faker("first_name_nonbinary")
    last_name = factory.Faker("last_name_nonbinary")
    gender = factory.Faker("random_element", elements=["M", "F"])
    birth_date = factory.Faker("date_of_birth", minimum_age=1, maximum_age=90)
    phone_number = factory.LazyAttribute(
        lambda _: (fake.country_calling_code() + fake.phone_number())[:14]
    )
