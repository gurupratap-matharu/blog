import json
import logging

from django import forms
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils.functional import cached_property
from django.utils.html import mark_safe, strip_tags

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import StreamField
from wagtail.models import Orderable
from wagtail.search import index

from base.blocks import BaseStreamBlock
from base.models import BasePage
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import Tag, TaggedItemBase

logger = logging.getLogger(__name__)


class BlogPersonRelationship(Orderable, models.Model):
    """
    This defines the relationship between the `Person` within the `base`
    app and the BlogPage below. This allows people to be added to a BlogPage.

    We have created a two way relationship between BlogPage and Person using
    the ParentalKey and ForeignKey
    """

    page = ParentalKey(
        "BlogPage", related_name="blog_person_relationship", on_delete=models.CASCADE
    )

    person = models.ForeignKey(
        "base.Person", related_name="person_blog_relationship", on_delete=models.CASCADE
    )

    panels = [FieldPanel("person")]

    class Meta:
        verbose_name = "blogpersonrelationship"


class BlogIndexPage(RoutablePageMixin, BasePage):
    page_description = "Use this page to show a list of blog posts"
    max_count = 1

    intro = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px to 3000px.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("image"),
    ]

    parent_page_types = ["home.HomePage"]

    # Specify that only blog pages can be children of this blogindex page
    subpage_types = ["BlogPage"]

    class Meta:
        verbose_name = "blogindexpage"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        qs = self.get_children().live().order_by("-first_published_at")

        paginator = Paginator(qs, 9)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["posts"] = context["page_obj"] = page_obj
        context["featured"] = qs.first()  # <- TODO: Improve this

        return context

    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        """
        Custom view that returns all BlogPages for a given tag and redirect back to the
        BlogIndexPage.

        Special thing is that it uses a different url structure as defined
        the method decorator.

        eg: /blog/tags/health/ <-- show all blog pages with `health` tag

        More information on RoutablePages is at
        https://docs.wagtail.org/en/stable/reference/contrib/routablepage.html
        """

        try:
            tag = Tag.objects.get(slug__iexact=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = f'There are no blog posts tagged with "{tag}"'
                messages.info(request, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {"tag": tag, "posts": posts}
        return render(request, "blog/blog_index_page.html", context)

    @route(r"^categories/$", name="category_archive")
    @route(r"^categories/([\w-]+)/$", name="category_archive")
    def category_archive(self, request, category=None):
        """
        Show posts only for a certain category.
        """

        try:
            category = BlogCategory.objects.get(name__iexact=category)
        except BlogCategory.DoesNotExist:
            if category:
                msg = f'There are no blog posts of category "{category}"'
                messages.info(request, msg)
            return redirect(self.url)

        posts = self.get_posts().filter(categories=category)

        context = {"category": category, "posts": posts}
        return render(request, "blog/blog_index_page.html", context)

    def get_posts(self, tag=None):
        """
        Returns the child BlogPage objects for this BlogIndexPage.
        If a tag is used then it will filter the posts by tag.
        """

        posts = BlogPage.objects.live().descendant_of(self)
        posts = posts.filter(tags=tag) if tag else posts
        return posts


class BlogPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the BlogPage object and tags. There's a longer guide on using it at
    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging
    """

    content_object = ParentalKey(
        "BlogPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class BlogPage(BasePage):
    """
    A Blog Page or a single Blog Post

    We access the Person object with an inline panel that references the
    ParentalKey's `related_name` in BlogPersonRelationship. More docs:
    https://docs.wagtail.org/en/stable/topics/pages.html#inline-models
    """

    page_description = "Use this page to write a single blog post"

    subtitle = models.CharField(max_length=255, blank=True)
    intro = models.CharField(
        help_text="Text to describe the page", max_length=500, blank=True
    )
    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px to 3000px",
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date", blank=True, null=True)
    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("date"),
    ]

    content_panels = BasePage.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("intro"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "blog_person_relationship",
                    heading="Authors",
                    label="Author",
                    panels=None,
                    min_num=1,
                    help_text="Select between one and three authors",
                ),
                FieldPanel("date"),
                FieldPanel("tags"),
                FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
            ],
            heading="Blog information",
        ),
        InlinePanel("gallery_images", label="Gallery images"),
        InlinePanel("related_links", heading="Related links", label="Related links"),
    ]

    promote_panels = [
        MultiFieldPanel(BasePage.promote_panels, "Common page configuration"),
        FieldPanel("feed_image"),
    ]

    # Specifies parent to BlogPage as being BlogIndexPages
    parent_page_types = ["blog.BlogIndexPage"]

    # Specifies what content types can exist as children of BlogPage.
    # Empty list means that no child content types are allowed.
    subpage_types = []

    class Meta:
        verbose_name = "blogpage"
        verbose_name_plural = "blogpages"

    def main_image(self):
        gallery_item = self.gallery_images.first()

        return gallery_item.image if gallery_item else None

    @cached_property
    def get_tags(self):
        """
        Find all the tags that are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """

        base_url = self.get_parent().url
        tags = self.tags.all()

        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"

        return tags

    def get_similar_posts(self):
        """
        Using tags find posts most similar to this one.
        """

        post_tags_ids = self.tags.values_list("id", flat=True)
        similar_posts = BlogPage.objects.filter(tags__in=post_tags_ids).exclude(
            id=self.id
        )
        similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
            "-same_tags"
        )[:3]
        return similar_posts

    def authors(self):
        """
        Returns the BlogPage's related people.
        We are using the ParentalKey's `related_name` from the BlogPersonRelationship model
        to access these objects. This allows us to access the Person objects
        with a loop on the template.

        If we tried to access the blog_person_relationship directly we'd print `blog.BlogPersonRelationship.None`
        """
        # Only return authors that are not in draft
        return [
            n.person
            for n in self.blog_person_relationship.filter(
                person__live=True
            ).select_related("person")
        ]

    def canonical_url(self):
        # Veer customise this incase of multiple routes
        return self.get_full_url()

    @cached_property
    def reading_time(self):
        """
        Divide the word count by avg reading speed of 200 words per minute.
        """
        text = strip_tags(self.body.raw_data)
        words = len(text.split(" "))
        return round(words / 200)

    def ld_entity(self):
        image = self.feed_image or self.listing_image or self.social_image
        image_url = image.file.url if image else ""

        image_schema = {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "contentUrl": f"https://ventanita.com.ar{image_url}",
            "license": "https://ventanita.com.ar/condiciones-generales/",
            "acquireLicensePage": "https://ventanita.com.ar/contact/",
            "creditText": image.description or self.listing_title or self.social_text,
            "creator": {"@type": "Organisation", "name": "Ventanita"},
            "copyrightNotice": "Ventanita",
        }

        article_schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "url": self.full_url,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.full_url,
            },
            "headline": self.title,
            "description": self.search_description,
            "image": f"https://ventanita.com.ar{image_url}",
            "author": {"@type": "Person", "name": self.authors()[0].full_name()},
            "publisher": {
                "@type": "Organization",
                "name": "Ventanita",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://ventanita.com.ar/static/assets/img/logos/ventanita.avif",
                },
            },
            "datePublished": self.first_published_at.isoformat(),
            "dateModified": self.last_published_at.isoformat(),
        }

        page_schema = json.dumps(
            {
                "@context": "http://schema.org",
                "@graph": [image_schema, article_schema],
            },
            ensure_ascii=False,
        )
        return mark_safe(page_schema)


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

    class Meta:
        verbose_name = "blogpagegallery"
        verbose_name_plural = "blogpagegalleries"


class BlogPageRelatedLink(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name="related_links")
    name = models.CharField(max_length=255)
    url = models.URLField()

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
    ]

    class Meta:
        verbose_name = "blogpagerelatedlink"
        verbose_name_plural = "blogpagerelatedlinks"

    def __str__(self):
        return f"{self.name} | {self.url}"


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
        verbose_name = "blogcategory"
        verbose_name_plural = "blog categories"
