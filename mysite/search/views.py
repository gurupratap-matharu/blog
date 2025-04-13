import logging

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from wagtail.models import Locale, Page

logger = logging.getLogger(__name__)


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        search_results = (
            Page.objects.live().filter(locale=Locale.get_active()).search(search_query)
        )
    else:
        search_results = Page.objects.none()

    paginator = Paginator(search_results, 10)

    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    context = dict()
    context["search_query"] = search_query
    context["search_results"] = search_results

    return render(request, "search/search.html", context)
