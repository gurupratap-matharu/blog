from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.validators import validate_birth_date


class ValidatorsTests(SimpleTestCase):
    def test_very_old_person_raises_exception(self):
        # Arrange
        hundred_years_ago = date.today() - timedelta(days=365 * 101)

        # Act + Assert
        with self.assertRaises(ValidationError):
            validate_birth_date(hundred_years_ago)

    def test_normal_person_is_ok(self):
        """
        For valid date no exception should be raise so we simply
        run the method without asserting anything.
        """

        # Arrange
        thirty_years_ago = date.today() - timedelta(days=365 * 30)

        # Act + No Assert
        validate_birth_date(thirty_years_ago)

    def test_person_who_is_not_born(self):
        # Arrange
        next_year = date.today() + timedelta(days=365)

        # Act + Assert
        with self.assertRaises(ValidationError):
            validate_birth_date(next_year)
