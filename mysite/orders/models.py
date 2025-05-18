import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from .validators import phone_regex, validate_birth_date


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    passengers = models.ManyToManyField("Passenger", related_name="+")

    name = models.CharField(_("Nombre"), max_length=50)
    email = models.EmailField(
        _("Email"), help_text=_("Enviaremos los pasajes a este email")
    )
    phone_number = models.CharField(
        _("Telefono"), validators=[phone_regex], max_length=17
    )
    paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=250, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        indexes = [
            models.Index(fields=["-created_on"]),
        ]

    def __str__(self):
        return f"{self.name}"


class Passenger(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ("DNI", "DNI"),
        ("PASSPORT", "PASSPORT"),
        ("CE", "CEDULA"),
        ("LE", "LE"),
        ("LC", "LC"),
        ("CUIT", "CUIT"),
        ("NIE", "NIE"),
        ("RG", "RG"),
        ("RNE", "RNE"),
        ("CPF", "CPF"),
        ("RUT", "RUT"),
        ("CURP", "CURP"),
        ("CNPJ", "CNPJ"),
    ]

    GENDER_CHOICES = [
        ("F", _("Female")),
        ("M", _("Male")),
    ]

    document_type = models.CharField(
        _("Tipo de documento"), choices=DOCUMENT_TYPE_CHOICES, max_length=10
    )
    document_number = models.CharField(
        _("Nro de documento"), max_length=50, unique=True
    )
    nationality = CountryField(_("Nacionalidad"), blank_label=_("(Nationality)"))
    first_name = models.CharField(_("Nombre"), max_length=50)
    last_name = models.CharField(_("Apellido"), max_length=50)
    gender = models.CharField(_("Género"), choices=GENDER_CHOICES, max_length=1)
    birth_date = models.DateField(
        _("Fecha de nacimiento"), validators=[validate_birth_date]
    )

    phone_number = models.CharField(
        _("Telefono"), validators=[phone_regex], max_length=17
    )

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = _("passenger")
        verbose_name_plural = _("passengers")
        indexes = [
            models.Index(fields=["-created_on"]),
        ]

    def __str__(self):
        return f"{self.first_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
