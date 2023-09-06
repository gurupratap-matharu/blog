from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    EmailBlock,
    ListBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


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
        icon = "comment-add"


class FAQBlock(StructBlock):
    item = ListBlock(FAQItemBlock())

    class Meta:
        icon = "comment"
        template = "blocks/faq_block.html"


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
