from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse_lazy

from .views import search


class SearchViewTests(TestCase):
    """
    Test suite for the search functionality of our project.
    """

    template_name = "search/search.html"
    url = reverse_lazy("search")

    def test_search_view_works(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, "Buscar")
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_search_view_resolves_correct_url(self):
        response = self.client.get(self.url)

        self.assertEqual(response.resolver_match.func, search)

    def test_search_view_with_invalid_query_shows_no_results(self):
        response = self.client.get(self.url, query_params={"query": "123"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "No results found")
