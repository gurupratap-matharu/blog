import logging
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from .validators import phone_regex, validate_birth_date

logger = logging.getLogger(__name__)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    passengers = models.ManyToManyField("Passenger", related_name="+")

    name = models.CharField(_("Nombre"), max_length=50)
    email = models.EmailField(
        _("Email"), help_text=_("Enviaremos los pasajes a este email")
    )
    phone_number = models.CharField(
        _("Telefono"),
        help_text="Ex: +5491150254321",
        validators=[phone_regex],
        max_length=17,
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

    def confirm(self, payment_id):
        logger.info("confirming order...")

        if not payment_id:
            raise ValidationError(
                "Order: %(order)s cannot be confirmed without a payment_id!",
                params={"order": self},
                code="invalid",
            )

        self.paid = True
        self.payment_id = payment_id
        self.save(update_fields=["paid", "payment_id"])

        return self

    def send_mail(self):

        return send_mail(
            _("Pasajes Confirmados"),
            _("Gracias por tu compra"),
            settings.DEFAULT_FROM_EMAIL,
            [self.email, settings.DEFAULT_TO_EMAIL],
            fail_silently=False,
        )

    def send_confirmation(self, payment_id):
        self.confirm(payment_id)
        self.send_mail()


class Passenger(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ("DNI", "DNI"),
        ("PP", "PASSPORTE"),
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

    FEMALE = "F"
    MALE = "M"
    GENDER_CHOICES = [
        (FEMALE, _("Female")),
        (MALE, _("Male")),
    ]

    document_type = models.CharField(
        _("Tipo de documento"),
        choices=DOCUMENT_TYPE_CHOICES,
        max_length=10,
        default="DNI",
    )
    document_number = models.CharField(
        _("Nro de documento"), max_length=50, unique=True
    )
    nationality = CountryField(_("Nacionalidad"), blank_label=_("(Nationality)"))
    first_name = models.CharField(_("Nombre"), max_length=50)
    last_name = models.CharField(_("Apellido"), max_length=50)
    gender = models.CharField(
        _("Género"), choices=GENDER_CHOICES, max_length=1, default=FEMALE
    )
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

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.birth_date.strftime("%Y-%m-%d"),
            "gender": self.gender,
            "document_type": self.document_type,
            "document_number": self.document_number,
            "nationality": self.nationality.code,
            "phone_number": self.phone_number,
        }
