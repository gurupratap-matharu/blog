import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .validators import phone_regex, validate_birth_date

logger = logging.getLogger(__name__)


class OrderForm(forms.Form):
    name = forms.CharField(
        label=_("Nombre"),
        min_length=3,
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label=_("Correo Electrónico"),
        help_text=_("Enviaremos los pasajes a este email"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    confirm_email = forms.EmailField(
        label=_("Confirmar Correo Electrónico"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone_number = forms.CharField(
        label=_("Telefono"),
        validators=[phone_regex],
        help_text=_("Eg: +5491150254191"),
        max_length=17,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.errors:
            attrs = self[field].field.widget.attrs
            attrs.setdefault("class", "")
            attrs["class"] += " is-invalid"

    def clean(self):
        cd = super().clean()

        email = cd.get("email")
        confirm_email = cd.get("confirm_email")

        if email != confirm_email:
            msg = _("Las direcciones de correo electrónico no coinciden")
            err = ValidationError(msg, code="invalid")
            self.add_error("confirm_email", err)


class PassengerForm(forms.Form):

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
        ("O", _("Other")),
    ]

    SELECT = forms.Select(attrs={"class": "form-select"})
    TEXT = forms.TextInput(attrs={"class": "form-control"})

    document_type = forms.ChoiceField(
        label=_("Tipo de documento"), choices=DOCUMENT_TYPE_CHOICES, widget=SELECT
    )
    document_number = forms.CharField(
        label=_("Nro de documento"), min_length=5, max_length=50, widget=TEXT
    )
    nationality = CountryField(blank_label=_("(Nacionalidad)")).formfield(widget=SELECT)

    first_name = forms.CharField(
        label=_("Nombre"), min_length=3, max_length=50, widget=TEXT
    )
    last_name = forms.CharField(
        label=_("Apellido"), min_length=3, max_length=50, widget=TEXT
    )
    gender = forms.ChoiceField(
        label=_("Género"),
        choices=GENDER_CHOICES,
        widget=SELECT,
    )
    birth_date = forms.DateField(
        label=_("Fecha de nacimiento"),
        initial="mm/dd/yyyy",
        validators=[validate_birth_date],
        widget=forms.DateInput(attrs={"class": "form-control"}),
    )
    phone_number = forms.CharField(
        label=_("Teléfono"),
        validators=[phone_regex],
        help_text=_("Eg: +5491150254191"),
        max_length=17,
        widget=TEXT,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.errors:
            attrs = self[field].field.widget.attrs
            attrs.setdefault("class", "")
            attrs["class"] += " is-invalid"
