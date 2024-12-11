from django.views.genertic import TemplateView


class HelpSearchView(TemplateView):
    template_name = "help/help_search.html"
