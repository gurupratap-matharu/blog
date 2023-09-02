import logging

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page

logger = logging.getLogger(__name__)


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    logger.info("search query:%s" % search_query)
    logger.info("page:%s" % page)

    # Search
    if search_query:
        search_results = Page.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
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
