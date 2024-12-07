from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField

from base.blocks import BaseStreamBlock, FAQBlock, ImageLinkBlock, LinkBlock, PromotionsBlock
from base.models import BasePage


class HomePage(BasePage):
    """
    The Home Page is a dynamic page which has different sections that link to other pages
    on the site. Broadly it has the following sections
        - Hero area + search form
        - Featured sections
        - A promotional area
        - Body area
        - CTA section
    """

    page_description = "Use this page to build the home page"

    # Hero section of HomePage
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Homepage image",
    )
    hero_text = models.CharField(max_length=255, help_text="Keep it short and powerful")
    hero_cta = models.CharField(
        verbose_name="Hero CTA",
        max_length=255,
        help_text="Text to display on Call to Action",
    )
    hero_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Hero CTA link",
        help_text="Choose a page to link to for the Call to Action",
    )

    body = StreamField(
        BaseStreamBlock(),
        blank=True,
        use_json_field=True,
    )

    promotions = StreamField(
        [("promotions", PromotionsBlock())],
        verbose_name="Promotions Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    # Featured sections on the HomePage
    # You will see on home/home_page.html that these are treated
    # in different ways, and displayed in different areas of the page.
    # Each list their children items that we access via the children function
    # that we define on the individual Page models e.g. BlogIndexPage
    featured_section_1_title = models.CharField(
        blank=True, max_length=255, help_text="Title to display above the promo copy"
    )
    featured_section_1 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="First featured section for the homepage. Will display up to three child items.",
        verbose_name="Featured section 1",
    )

    featured_section_2_title = models.CharField(
        blank=True, max_length=255, help_text="Title to display above the promo copy"
    )
    featured_section_2 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Second featured section for the homepage. Will display up to three child items.",
        verbose_name="Featured section 2",
    )

    featured_section_3_title = models.CharField(
        blank=True, max_length=255, help_text="Title to display above the promo copy"
    )
    featured_section_3 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Third featured section for the homepage. Will display up to six child items.",
        verbose_name="Featured section 3",
    )

    featured_pages = StreamField(
        [("featured", ImageLinkBlock())],
        verbose_name="Popular Destinations Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    faq = StreamField(
        [("faq", FAQBlock())],
        verbose_name="FAQ Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    links = StreamField(
        [("Links", LinkBlock())],
        verbose_name="Links Section",
        blank=True,
        max_num=1,
        use_json_field=True,
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("hero_text"),
                MultiFieldPanel(
                    [
                        FieldPanel("hero_cta"),
                        FieldPanel("hero_cta_link"),
                    ]
                ),
            ],
            heading="Hero section",
        ),
        FieldPanel("promotions"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_1_title"),
                        FieldPanel("featured_section_1"),
                    ]
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_2_title"),
                        FieldPanel("featured_section_2"),
                    ]
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("featured_section_3_title"),
                        FieldPanel("featured_section_3"),
                    ]
                ),
            ],
            heading="Featured homepage sections",
        ),
        FieldPanel("featured_pages"),
        FieldPanel("faq"),
        FieldPanel("links"),
    ]

    class Meta:
        verbose_name = "homepage"
        verbose_name_plural = "homepages"

    def __str__(self):
        return self.title
