import logging
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,17}$",
    message=_(
        "El número de teléfono debe tener el formato '+5491150251122'. Se permiten hasta 17 dígitos."
    ),
)


def validate_birth_date(born):
    """Check if a person is between 1 - 99 years old"""

    today = date.today()
    age = (
        today.year
        - born.year
        - ((today.month, today.day) < (born.month, born.day))
    )

    logger.info("validating birth date:%s", born)
    logger.info("age:%s", age)

    if born > today:
        raise ValidationError(
            _("Your birth date (%(value)s) cannot be in the future!"),
            code="invalid",
            params={"value": born},
        )

    if age > 99:
        raise ValidationError(
            _("%(value)s doesn't seem right. Age is %(age)s years!"),
            code="invalid",
            params={"value": born, "age": age},
        )
