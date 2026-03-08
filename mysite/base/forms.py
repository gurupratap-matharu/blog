import logging

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class ReasonChoices(models.TextChoices):
    IMPRECISE = (
        "IMPRECISE",
        _("Impreciso: no coincide con el hecho actual o esta desactualizado"),
    )
    DIFFICULT = (
        "DIFFICULT",
        _("Difícil de entender: traducción poco clara o incorrecta"),
    )
    INCOMPLETE = (
        "INCOMPLETE",
        _("Falta información: es relevante pero no está completa"),
    )
    ERRONEOUS = (
        "ERRONEOUS",
        _(
            "Errores menores: problemas de formato, errores ortográficos y vínculos rotos"
        ),
    )
    OTHER = (
        "OTHER",
        _("Otras sugerencias: ideas para mejorar el contenido"),
    )


class PageFeedbackForm(forms.Form):
    """
    Generic form we use on wagtail pages to make improvements.
    """

    template_name = "base/forms/div.html"

    url = forms.CharField(widget=forms.HiddenInput)

    reason = forms.ChoiceField(
        label=_("Seleccioná uno"),
        choices=ReasonChoices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    message = forms.CharField(
        label=_("Comentarios"),
        min_length=10,
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "cols": 20}
        ),
    )

    def send_mail(self):
        cd = self.cleaned_data
        subject = f"[Ventanita] Page Feedback for {cd['url']}"
        message = (
            f"URL:{cd['url']}\nReason:{cd['reason']}\nmessage:{cd['message']}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_TO_EMAIL],
        )
