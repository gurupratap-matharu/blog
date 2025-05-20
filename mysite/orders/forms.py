import logging

from django import forms
from django.core.exceptions import ValidationError
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
