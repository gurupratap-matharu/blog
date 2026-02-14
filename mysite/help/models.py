import logging

from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from base.blocks import BaseStreamBlock
from base.models import BasePage, GenericImportantPages


logger = logging.getLogger(__name__)


class HelpIndexPage(BasePage):
    """
    A collection of help article pages under the same topic.
    """

    page_description = (
        "Use this page to show a list of help articles under the same topic"
    )

    subtitle = models.CharField(max_length=255, blank=True)

    content_panels = BasePage.content_panels + [FieldPanel("subtitle")]

    subpage_types = ["HelpArticlePage"]

    class Meta:
        verbose_name = "helpindexpage"
        verbose_name_plural = "helpindexpages"

    def get_articles(self):
        qs = self.get_children().live().order_by("-first_published_at")
        return qs


class HelpArticlePage(BasePage):
    """
    A single help article on our platform.
    """

    page_description = "Use this page to write a single help article"
    subtitle = models.CharField(max_length=255, blank=True)

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page Body", blank=True, collapsed=True
    )
    date = models.DateField("Post date", blank=True, null=True)

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
        index.SearchField("date"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("body"),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["help.HelpIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "helparticlepage"
        verbose_name_plural = "helparticlepages"

    def get_related_articles(self):
        """Fetch all the siblings of the page except the page itself"""

        return self.get_siblings(inclusive=False)

    def get_context(self, request, *args, **kwargs):
        """
        Add article feedback form to context.
        """

        context = super().get_context(request, *args, **kwargs)

        imp_pages = GenericImportantPages.load(request_or_site=request)

        try:
            feedback_page = imp_pages.article_feedback_page.get_specific()
            form = feedback_page.get_form(initial={"page_url": self.url})
        except AttributeError as e:
            logger.warning("%s article feedback form page not linked..." % e)
            form = None

        context["article_feedback_form"] = form
        context["article_feedback_page"] = feedback_page

        return context
