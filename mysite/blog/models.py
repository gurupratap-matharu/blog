import logging

from django import forms
from django.core.paginator import Paginator
from django.db import models

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from bs4 import BeautifulSoup
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase

from blog.blocks import CommonContentBlock

logger = logging.getLogger(__name__)


class BlogIndexPage(Page):
    page_description = "Use this page to show a list of blog posts"
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("intro")]

    class Meta:
        verbose_name = "blogindexpage"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        qs = self.get_children().live().order_by("-first_published_at")

        paginator = Paginator(qs, 9)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["posts"] = context["page_obj"] = page_obj
        context["featured"] = qs.first()
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "BlogPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class BlogTagIndexPage(Page):
    page_description = "Use this page to list blog posts by a tag"

    class Meta:
        verbose_name = "Blog Tag Index Page"

    def get_context(self, request, *args, **kwargs):
        tag = request.GET.get("tag")
        blogpages = BlogPage.objects.filter(tags__name=tag)

        context = super().get_context(request, *args, **kwargs)
        context["blogpages"] = blogpages

        return context


class BlogPage(Page):
    page_description = "Use this page to write a single blog post"

    author = models.CharField(max_length=255)
    date = models.DateField("Post date", blank=True, null=True)
    intro = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)

    body = StreamField(
        CommonContentBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px to 3000px",
    )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("date"),
    ]
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("author"),
                FieldPanel("date"),
                FieldPanel("tags"),
                FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
            ],
            heading="Blog information",
        ),
        FieldPanel("intro"),
        FieldPanel("subtitle"),
        FieldPanel("body"),
        InlinePanel("gallery_images", label="Gallery images"),
        InlinePanel("related_links", heading="Related links", label="Related links"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        FieldPanel("feed_image"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "blogpage"

    def main_image(self):
        gallery_item = self.gallery_images.first()

        return gallery_item.image if gallery_item else None

    def toc(self):
        """Get table of contents for a page"""
        bs = BeautifulSoup(self.body)
        return [e.get_text().strip() for e in bs.find_all("h2")]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(
        BlogPage, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )
    caption = models.CharField(blank=True, max_length=250)
    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class BlogPageRelatedLink(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name="related_links")
    name = models.CharField(max_length=255)
    url = models.URLField()

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
    ]


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    panels = [
        FieldPanel("name"),
        FieldPanel("icon"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "blog categories"
