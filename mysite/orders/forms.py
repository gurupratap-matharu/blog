import logging
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import mail_admins
from django.utils.translation import gettext_lazy as _

from .models import Order, Passenger

logger = logging.getLogger(__name__)


class OrderForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        label=_("Confirmar Correo Electrónico"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.errors:
            attrs = self[field].field.widget.attrs
            attrs.setdefault("class", "")
            attrs["class"] += " is-invalid"

    class Meta:
        model = Order
        fields = ("name", "phone_number", "email")

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cd = super().clean()
        email = cd.get("email")
        confirm_email = cd.get("confirm_email")

        if email != confirm_email:
            msg = _("Las direcciones de correo electrónico no coinciden")
            err = ValidationError(msg, code="invalid")
            self.add_error("confirm_email", err)


class PassengerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.errors:
            attrs = self[field].field.widget.attrs
            attrs.setdefault("class", "")
            attrs["class"] += " is-invalid"

    class Meta:
        model = Passenger
        exclude = ("created_on", "updated_on")

        select = {"class": "form-select", "required": "required"}
        control = {"class": "form-control", "required": "required"}
        widgets = {
            "document_type": forms.Select(attrs=select),
            "document_number": forms.TextInput(attrs=control),
            "first_name": forms.TextInput(attrs=control),
            "last_name": forms.TextInput(attrs=control),
            "birth_date": forms.DateInput(
                attrs={"type": "date", **control},
            ),
            "phone_number": forms.TextInput(
                attrs={"placeholder": _("Whatsapp"), "type": "tel", **control}
            ),
            "nationality": forms.Select(attrs=select),
            "gender": forms.Select(attrs=select),
        }


class OrderCancelForm(forms.Form):
    DOCUMENT_TYPE_CHOICES = [
        ("DNI", "DNI"),
        ("Passport", "Pasaporte"),
        ("Other", "Otros"),
    ]

    document_type = forms.ChoiceField(
        label=_("Tipo de documento"),
        required=True,
        choices=DOCUMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    document_number = forms.CharField(
        label=_("Número de documento"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    travel_date = forms.DateField(
        label=_("Fecha de viaje"),
        input_formats=["%d-%m-%Y"],
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control travel-date"}),
    )

    invoice_number = forms.CharField(
        label=_("Número del comprobante"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.errors:
            attrs = self[field].field.widget.attrs
            attrs.setdefault("class", "")
            attrs["class"] += " is-invalid"

    def clean_travel_date(self):
        """
        Allow travel date in the future only since past tickets cannot be cancelled.
        """

        data = self.cleaned_data["travel_date"]

        logger.info("checking travel date is in future...")
        logger.info("travel_date:%s" % data)

        if data < datetime.today().date():
            raise ValidationError(
                _("Fecha de ida:%(value)s no puede ser en el pasado"),
                code="invalid",
                params={"value": data},
            )

        return data

    def send_mail(self):
        logger.info("sending order cancel email...")
        cd = self.cleaned_data

        subject = f"Devolución: {cd['invoice_number']}"
        message = (
            f"Doc type:{cd['document_type']}\n"
            f"Doc no  :{cd['document_number']}\n"
            f"Travel  :{cd['travel_date'].strftime('%d-%m-%Y')}\n"
            f"Invoice :{cd['invoice_number']}\n"
            f"Email   :{cd['email']}\n"
        )

        mail_admins(subject, message)
