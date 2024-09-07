import logging
from os.path import splitext

from django.contrib import messages
from django.db import models
from django.forms import widgets
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractEmailForm,
    AbstractFormField,
)
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model
from wagtail.images.fields import WagtailImageField
from wagtail.models import (
    Collection,
    DraftStateMixin,
    LockableMixin,
    Page,
    PreviewableMixin,
    RevisionMixin,
    TranslatableMixin,
    WorkflowMixin,
)
from wagtail.search import index

from base.blocks import BaseStreamBlock
from base.views import CustomSubmissionsListView
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

logger = logging.getLogger(__name__)

ImageModel = get_image_model()


class Country(models.Model):
    """
    A Django model to store set of countries of origin.

    In the PartnerPage, StationPage models we'll use a ForeignKey to create the relationship between
    Country and other models. This allows a single relationship (e.g only one
    Country can be added) that is one-way (e.g. Country will have no way to
    access related objects).
    """

    title = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Country of Origin"
        verbose_name_plural = "Countries of Origin"

    def __str__(self):
        return self.title


class Person(
    WorkflowMixin,
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    PreviewableMixin,
    index.Indexed,
    ClusterableModel,
):
    """
    A model to store Person objects.

    It is registered using the `register_snippet` as a function in wagtail_hooks.py

    `Person` uses the `ClusterableModel`, which allows the relationship with another
    model to be stored locally to the 'parent' model (e.g. a PageModel) until the parent
    is explicitly saved. This allows the editor to use the 'Preview' button, to preview
    the content without saving the relationship to the database first.

    Read more at https://github.com/wagtail/django-modelcluster
    """

    first_name = models.CharField("First name", max_length=254)
    last_name = models.CharField("Last name", max_length=254)
    job_title = models.CharField("Job title", max_length=254)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("first_name"),
                        FieldPanel("last_name"),
                    ]
                )
            ],
            "Name",
        ),
        FieldPanel("job_title"),
        FieldPanel("image"),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("first_name"),
        index.SearchField("last_name"),
        index.FilterField("job_title"),
        index.AutocompleteField("first_name"),
        index.AutocompleteField("last_name"),
    ]

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def thumb_image(self):
        """
        Generate a square html tag for this person if he/she has an image uploaded.

        Ex: '<img alt="kal-visuals-square" height="50" width="50"
                src="/media/images/kal-visuals-square.2e16d0ba.fill-50x50.jpg">'
        """

        return self.image.get_rendition("fill-50x50").img_tag() if self.image else ""

    @property
    def preview_modes(self):
        return PreviewableMixin.DEFAULT_PREVIEW_MODES + [("blog_post", _("Blog post"))]

    def get_preview_template(self, request, mode_name):
        """Html template to render the person model in UI"""

        # TODO: see conditional rendering for this in bakery demo
        return "base/preview/person.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)

        # TODO: yet to be completed. refer bakerydemo

        return context


class FooterText(
    DraftStateMixin, RevisionMixin, PreviewableMixin, TranslatableMixin, models.Model
):
    """
    Site footer text which is registered using the `register_snippet` in `wagtail_hooks.py`.
    It is made accessible on the template via a template tag defined in `navigation_tags.py`
    """

    body = RichTextField()

    panels = [
        FieldPanel("body"),
        PublishingPanel(),
    ]

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Footer Text"

    def __str__(self):
        return "Footer Text"

    def get_preview_template(self, request, mode_name):
        return "base.html"

    def get_preview_context(self, request, mode_name):
        return {"footer_text": self.body}


class StandardPage(Page):
    """
    A generic content page which we can use for any page that only needs a title, image, introduction and a body field.

    Some examples are typical static pages like
    about, terms, privacy, etc.
    """

    page_description = "Use this to build a simple or generic page"

    introduction = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px to 3000px.",
    )

    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image"),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "standard page"
        verbose_name_plural = "standard pages"

    def __str__(self):
        return self.title


class FormField(AbstractFormField):
    """
    One FormPage can have many FormFields. Here we declare the parentalkey (foreign key)
    for our form.
    """

    field_type = models.CharField(
        verbose_name="field type",
        max_length=16,
        choices=list(FORM_FIELD_CHOICES) + [("image", "Upload Image")],
    )

    page = ParentalKey("FormPage", related_name="form_fields", on_delete=models.CASCADE)


class CustomFormBuilder(FormBuilder):
    def create_image_field(self, field, options):
        return WagtailImageField(**options)


class FormPage(AbstractEmailForm):
    page_description = "Use this page to create a simple form"
    form_builder = CustomFormBuilder
    submissions_list_view_class = CustomSubmissionsListView

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(BaseStreamBlock(), use_json_field=True, blank=True)
    thank_you_text = RichTextField(blank=True)

    uploaded_image_collection = models.ForeignKey(
        "wagtailcore.Collection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Veer note how we include the FormField obj via an InlinePanel using the
    # related_name value
    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("image"),
        FieldPanel("body"),
        InlinePanel("form_fields", heading="Form fields", label="Field"),
        FieldPanel("thank_you_text"),
        FieldPanel("uploaded_image_collection"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address"),
                        FieldPanel("to_address"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
    ]

    class Meta:
        verbose_name = "formpage"
        verbose_name_plural = "formpages"

    def get_context(self, request, *args, **kwargs):
        """
        Find if the form on this page instance has an image upload in it.
        """

        context = super().get_context(request, *args, **kwargs)
        context["has_upload"] = any(
            f.field_type == "image" for f in self.form_fields.all()
        )
        return context

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        for name, field in form.fields.items():
            if isinstance(field.widget, widgets.Textarea):
                field.widget.attrs.update({"rows": "5"})

            if isinstance(field.widget, widgets.Select):
                field.widget.attrs.update({"class": "form-select"})

            attrs = field.widget.attrs
            css_classes = attrs.get("class", "").split()
            css_classes.append("form-control")
            attrs.update({"class": " ".join(css_classes)})

        return form

    @staticmethod
    def get_image_title(filename):
        """
        Generates a usable title from the filename of an image upload.
        Note: The filename will be provided as a 'path/to/file.jpg'
        """

        if not filename:
            return

        result = splitext(filename)[0]
        result = result.replace("-", " ").replace("_", " ").title()

        logger.info("image_title: %s" % result)

        return result.title()

    def get_uploaded_image_collection(self):
        """
        Returns a Wagtail Collection, using this form's saved value if present,
        otherwise returns the 'Root' Collection.
        """

        collection = self.uploaded_image_collection
        return collection or Collection.get_first_root_node()

    def process_form_submission(self, form):
        """
        If an Image upload is found, pull out the files data, create an actual
        Wagtail Image and reference its ID in the stored form response.
        """

        cleaned_data = form.cleaned_data

        for name, field in form.fields.items():
            if isinstance(field, WagtailImageField):
                image_file_data = cleaned_data[name]

                if image_file_data:
                    kwargs = {
                        "file": cleaned_data[name],
                        "title": self.get_image_title(cleaned_data[name].name),
                        "collection": self.get_uploaded_image_collection(),
                    }

                    if form.user and not form.user.is_anonymous:
                        kwargs["uploaded_by_user"] = form.user

                    logger.info("kwargs:%s" % kwargs)
                    logger.info("creating image...")

                    image = ImageModel(**kwargs)
                    image.save()
                    # saving the image id
                    # alternatively we can store a path to the image via image.get_rendition

                    logger.info("created image:%s..." % image.pk)

                    cleaned_data.update({name: image.pk})

                else:
                    # remove the value from the data
                    logger.warn("image_file_data is None...")
                    del cleaned_data[name]

        submission = self.get_submission_class().objects.create(
            form_data=cleaned_data, page=self
        )

        logger.info("submission:%s" % submission)

        # important: if extending AbstractEmailForm, email logic must be re-added here
        if self.to_address:
            self.send_mail(form)

        return submission

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        """
        Redirect user to home page after successful submission.
        """

        url = "/"
        # if a form_submission instance is available, append the id to URL
        # when previewing landing page, there will not be a form_submission instance
        if form_submission:
            url += "?id=%s" % form_submission.id

        messages.success(request, "Message sent successfully! 🙌")
        return redirect(url, permanent=False)


@register_setting
class GenericSettings(ClusterableModel, BaseGenericSetting):
    twitter_url = models.URLField(verbose_name="Twitter URL", blank=True)
    facebook_url = models.URLField(verbose_name="Facebook URL", blank=True)
    instagram_url = models.URLField(verbose_name="Instagram URL", blank=True)
    youtube_url = models.URLField(verbose_name="Youtube URL", blank=True)
    organisation_url = models.URLField(verbose_name="Organisation URL", blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("twitter_url"),
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("organisation_url"),
            ],
            "Social Links",
        )
    ]


@register_setting
class SiteSettings(BaseSiteSetting):
    title_suffix = models.CharField(
        verbose_name="Title suffix",
        max_length=255,
        help_text="The suffix for the title meta tag e.g. ' | Blog'",
        default="Book Bus tickets",
    )

    panels = [
        FieldPanel("title_suffix"),
    ]
