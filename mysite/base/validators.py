from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


validate_phone = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_(
        "Phone number must be entered in the format: '+5491150254191'. Up to 15 digits allowed."
    ),
)


validate_lat_lng = RegexValidator(
    regex=r"^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)$",
    message="Lat Long must be a comma-separated numeric lat and long",
    code="invalid_lat_long",
)
