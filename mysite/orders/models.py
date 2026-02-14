import logging
import string
import uuid
from timeit import default_timer as timer

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
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
    transaction_id = models.CharField(max_length=50, blank=True)
    reservation_code = models.CharField(max_length=50, blank=True)

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

    def get_absolute_url(self):
        raise ValueError("Please implement this")

    def get_cancel_url(self):
        return reverse_lazy("orders:order-cancel", kwargs={"id": self.id})

    def confirm(self, payment_id, guid):
        logger.info("confirming order...")

        if not payment_id or not guid:
            raise ValidationError(
                "Order: %(order)s cannot be confirmed without both a payment_id: %(payment_id)s and guid:%(guid)s!",
                params={"order": self, "payment_id": payment_id, "guid": guid},
                code="invalid",
            )

        self.paid = True
        self.payment_id = payment_id
        self.transaction_id = guid
        self.reservation_code = get_random_string(
            length=6, allowed_chars=string.ascii_uppercase
        )
        self.save(
            update_fields=[
                "paid",
                "payment_id",
                "transaction_id",
                "reservation_code",
            ]
        )

        return self

    def send_user_email(self, sale):
        """
        Send the buyer an email with tickets.
        """

        logger.info("sending confirmation email...")
        context = sale

        context["order"] = self

        start = timer()

        subject_path = "orders/emails/booking_confirmed_subject.txt"
        message_path = "orders/emails/booking_confirmed_message.txt"

        subject = render_to_string(subject_path, context).strip()
        message = render_to_string(message_path, context).strip()

        msg = EmailMultiAlternatives(
            subject,
            message,
            settings.NOTIFICATION_EMAIL,
            [self.email],
            cc=[settings.NOTIFICATION_EMAIL],
            reply_to=[settings.NOTIFICATION_EMAIL],
        )

        mails_sent = msg.send()
        end = timer()

        logger.info("took:%0.2f secs" % (end - start))

        return mails_sent

    def send_confirmation(self, payment_id, sale, guid):
        """
        Update the order with payment_id and send an email to the user.
        """

        self.confirm(payment_id=payment_id, guid=guid)
        self.send_user_email(sale=sale)

        return self


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
    nationality = CountryField(
        _("Nacionalidad"), blank_label=_("(Nationality)")
    )
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
