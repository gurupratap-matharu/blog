from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    page_description = "Use this page to show a home page"

    body = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("body")]

    class Meta:
        verbose_name = "homepage"
