from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, streamfield

from locations.models import CityIndexPage

from base.models import StandardPage
from blog.models import BlogIndexPage
from partners.models import PartnerIndexPage

from .models import HomePage


class HomePageTests(WagtailPageTestCase):
    """
    Test suite to check if home page works fine
    """

    template_name = "home/home_page.html"

    @classmethod
    def setUpTestData(cls):
        cls.root = Page.get_first_root_node()
        cls.home_page = HomePage(
            title="Home", hero_text="You can do it", hero_cta="Learn More"
        )
        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        cls.post_data = nested_form_data(
            {
                "title": "Ventanita",
                "body": streamfield([("text", "buy bus tickets")]),
                "promotions": streamfield([("text", "we have good promos")]),
                "featured_pages": streamfield([("text", "promotions")]),
                "faq": streamfield([("text", "your questions answered")]),
                "links": streamfield([("text", "contact us")]),
            }
        )

    def test_get(self):
        response = self.client.get(self.home_page.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_default_route(self):
        self.assertPageIsRoutable(self.home_page)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.home_page)

    def test_page_is_previewable(self):
        self.assertPageIsPreviewable(self.home_page, post_data=self.post_data)

    def test_editability(self):
        self.assertPageIsEditable(self.home_page, post_data=self.post_data)
