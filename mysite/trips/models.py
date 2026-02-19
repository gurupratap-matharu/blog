from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .choices import Country, Province


class Location(models.Model):
    """
    Represents any location where a trip can start or stop. This include
    origin, destination and all intermediate stops.

    In domain sense this can be a bus terminal for intercity buses.
    """

    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    abbr = models.CharField(
        verbose_name=_("abbr"),
        max_length=7,
        unique=True,
    )
    latitude = models.DecimalField(
        _("Latitude"), max_digits=22, decimal_places=16, null=True
    )
    longitude = models.DecimalField(
        _("Longitude"), max_digits=22, decimal_places=16, null=True
    )
    address_line1 = models.CharField(
        _("Address line 1"), max_length=128, blank=True
    )
    address_line2 = models.CharField(
        _("Address line 2"), max_length=128, blank=True
    )
    city = models.CharField(_("City"), max_length=64, blank=True)
    state = models.CharField(_("Province"), max_length=5, choices=Province)
    country = models.CharField(
        _("Country"), max_length=5, choices=Country, default=Country.ARGENTINA
    )
    postal_code = models.CharField(_("Postal Code"), max_length=10, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.code,)

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse_lazy(
            "locations:location-detail", kwargs={"slug": self.slug}
        )


class Stats(models.Model):
    """
    Holds statistics between a pair of locations. This could be information
    like duration, price, first & last departures between (origin, destination) pair.
    """

    origin = models.ForeignKey(
        "trips.Location",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
    )
    destination = models.ForeignKey(
        "trips.Location",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
    )

    first_departure = models.TimeField(_("First departure"), null=True)
    last_departure = models.TimeField(_("Last departure"), null=True)
    duration = models.DurationField(_("Duration"), null=True)

    price_economy = models.DecimalField(
        _("Price Economy"),
        max_digits=9,
        decimal_places=2,
        null=True,
        validators=[MinValueValidator(1)],
    )
    price_avg = models.DecimalField(
        _("Price Average"),
        max_digits=9,
        decimal_places=2,
        null=True,
        validators=[MinValueValidator(1)],
    )

    num_departures = models.PositiveIntegerField(
        _("Number of departures per day"), null=True
    )

    companies = models.CharField(_("companies"), max_length=200, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("stats")
        verbose_name_plural = _("stats")
        indexes = [
            models.Index(fields=["-created_on"]),
        ]

    def clean(self):
        """
        Don't allow duplicate (origin, destination) stats
        Don't allow stats between same origin, destination
        """

        if self.origin == self.destination:
            raise ValidationError(
                _(
                    "Stats cannot be created between same origin:destination pair!"
                ),
                code="invalid",
                params={
                    "origin": self.origin,
                    "destination": self.destination,
                },
            )

        qs = Stats.objects.filter(
            origin=self.origin, destination=self.destination
        )
        if qs.exists():
            raise ValidationError(
                _(
                    "Stats for pair (%(origin)s:%(destination)s) already exists!"
                ),
                code="invalid",
                params={
                    "origin": self.origin,
                    "destination": self.destination,
                },
            )

    def __str__(self):
        return f"{self.origin}:{self.destination}"

    def get_companies_list(self):
        companies = self.companies.replace("/", ",").replace("|", ",")
        return [x.strip() for x in companies.split(",")]

    def get_duration_display(self):
        hours, remaining_seconds = divmod(self.duration.seconds, 3600)
        mins = remaining_seconds // 60

        return f"{hours} hr {mins} min"
