import logging

from django import template

from base.models import FooterText


register = template.Library()

logger = logging.getLogger(__name__)


@register.inclusion_tag("tags/breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    """
    Custom template tag to render breadcrumbs snippets
    """

    page = context.get("self")
    request = context.get("request")

    if page is None or page.depth <= 2:
        ancestors = ()
    else:
        ancestors = page.get_ancestors(inclusive=True).filter(depth__gt=1)

    context_breadcrumb = dict(ancestors=ancestors, request=request)

    return context_breadcrumb


@register.inclusion_tag("base/includes/footer_text.html", takes_context=True)
def get_footer_text(context):
    """
    Either get the custom footer text from the context or get the one that's live and defined in the the admin settings.
    """

    footer_text = context.get("footer_text", "")

    if not footer_text:
        obj = FooterText.objects.filter(live=True).first()

        footer_text = obj.body if obj else ""
    return {"footer_text": footer_text}
