from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, streamfield

from base.models import StandardPage
from locations.models import CityIndexPage
from partners.models import PartnerIndexPage

from blog.models import BlogIndexPage

from .models import HomePage


class HomePageTests(WagtailPageTestCase):
    """
    Test suite to check if home page works fine
    """

    template_name = "home/home_page.html"

    @classmethod
    def setUpTestData(cls):
        try:
            default_home = Page.objects.get(title="Welcome to your new Wagtail site!")
            default_home.slug = "home-old"
            default_home.save_revision().publish()
            default_home.save()

        except Page.DoesNotExist:
            pass

        cls.root = Page.objects.get(id=1).specific
        cls.home_page = HomePage(
            title="Home", slug="home", hero_text="You can do it", hero_cta="Learn More"
        )
        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

    def _get_post_data(self):
        data = dict()
        data["title"] = "Ventanita"
        data["body"] = streamfield([("text", "buy bus tickets")])
        data["promotions"] = streamfield([("text", "we have good promos")])
        data["featured_pages"] = streamfield([("text", "promotions")])
        data["faq"] = streamfield([("text", "your questions answered")])
        data["links"] = streamfield([("text", "contact us")])

        return nested_form_data(data)

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
        post_data = self._get_post_data()
        self.assertPageIsPreviewable(self.home_page, post_data=post_data)

    def test_editability(self):
        post_data = self._get_post_data()
        self.assertPageIsEditable(self.home_page, post_data=post_data)

    def test_can_create_index_pages_under_home_page(self):
        self.assertCanCreateAt(parent_model=HomePage, child_model=StandardPage)
        self.assertCanCreateAt(parent_model=HomePage, child_model=BlogIndexPage)
        self.assertCanCreateAt(parent_model=HomePage, child_model=CityIndexPage)
        self.assertCanCreateAt(parent_model=HomePage, child_model=PartnerIndexPage)

    def test_cannot_create_wrong_children_or_parents_for_home_page(self):
        self.assertCanNotCreateAt(parent_model=BlogIndexPage, child_model=HomePage)
        self.assertCanNotCreateAt(parent_model=CityIndexPage, child_model=HomePage)
        self.assertCanNotCreateAt(parent_model=PartnerIndexPage, child_model=HomePage)
