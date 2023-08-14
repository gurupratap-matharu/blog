import logging

from django import template

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
