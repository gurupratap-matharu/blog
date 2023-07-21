from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class PersonBlock(blocks.StructBlock):
    first_name = blocks.CharBlock()
    surname = blocks.CharBlock()
    photo = ImageChooserBlock(required=False)
    biography = blocks.RichTextBlock()

    class Meta:
        icon = "user"


class CommonContentBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(form_classname="title")
    paragraph = blocks.TextBlock()
    image = ImageChooserBlock()
    gallery = blocks.ListBlock(ImageChooserBlock())
    link = blocks.URLBlock()
    embed = EmbedBlock(
        template="blog/blocks/embed.html",
    )
    email = blocks.EmailBlock()
    datetime = blocks.DateTimeBlock()
    date = blocks.DateBlock()
    time = blocks.TimeBlock()
    boolean = blocks.BooleanBlock()
    html = blocks.RawHTMLBlock()
    blockquote = blocks.BlockQuoteBlock(form_classname="blockquote")
    person = PersonBlock()
