from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    EmailBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from .struct_values import LinkStructValue


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select h2 - h4 sizes for headers.
    """

    heading_text = CharBlock(required=True)
    size = ChoiceBlock(
        choices=[
            ("", "Select a header size"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"


class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and attribution data.
    """

    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "blocks/image_block.html"


class InternalLinkBlock(StructBlock):
    title = CharBlock(
        required=False,
        help_text="Leave blank to use page's listing title.",
    )
    page = PageChooserBlock()

    class Meta:
        icon = "link"
        value_class = LinkStructValue


class ExternalLinkBlock(StructBlock):
    title = CharBlock()
    link = URLBlock()

    class Meta:
        icon = "link"
        value_class = LinkStructValue


class LinkStreamBlock(StreamBlock):
    """
    Allow editors to an internal page link or an external web link.
    """

    internal_link = InternalLinkBlock()
    external_link = ExternalLinkBlock()

    class Meta:
        label = "Link"
        icon = "link"
        min_num = 1
        max_num = 1


class BlockQuote(StructBlock):
    """
    Custom `StructBlock` that allows the user to attribute a quote to the author.
    """

    text = TextBlock()
    attribute_name = CharBlock(blank=True, required=False, label="e.g. Mary Berry")

    class Meta:
        icon = "openquote"
        template = "blocks/blockquote.html"


class FAQItemBlock(StructBlock):
    question = CharBlock(required=True)
    answer = TextBlock(required=True)

    class Meta:
        label = "Section"
        icon = "title"


class FAQBlock(StructBlock):
    title = CharBlock(default="Frequently asked questions")
    item = ListBlock(FAQItemBlock())

    class Meta:
        icon = "list-ol"
        template = "blocks/faq_block.html"


class LinkBlock(StructBlock):
    heading_text = CharBlock(required=True)
    item = ListBlock(InternalLinkBlock())

    class Meta:
        icon = "list-ol"
        template = "blocks/link_block.html"


class ContactBlock(StructBlock):
    phone = CharBlock()
    whatsapp = CharBlock()
    email = EmailBlock()
    address = TextBlock()
    website = URLBlock()

    class Meta:
        template = "blocks/contact_block.html"


class BaseStreamBlock(StreamBlock):
    """
    Define a custom block that `StreamField` will utilize.
    """

    heading_block = HeadingBlock()
    paragraph_block = RichTextBlock(
        icon="pilcrow", template="blocks/paragraph_block.html"
    )

    image_block = ImageBlock()
    gallery = ListBlock(ImageBlock(), template="blocks/gallery_block.html")
    block_quote = BlockQuote()
    embed_block = EmbedBlock(
        help_text="Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
        icon="media",
        template="blocks/embed_block.html",
    )
    faq = FAQBlock()
    document = DocumentChooserBlock(template="blocks/document_block.html")
    link = LinkStreamBlock()
