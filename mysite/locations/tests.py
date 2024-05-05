import logging

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from locations.models import CityIndexPage, CityPage

logger = logging.getLogger(__name__)


class CityIndexPageRoutabilityTests(WagtailPageTestCase):
    """
    Test suite for the city index page
    """

    @classmethod
    def setUpTestData(cls):
        try:
            default_home = Page.objects.filter(
                title="Welcome to your new Wagtail site!"
            )[0]
            default_home.slug = "home-old"
            default_home.save_revision().publish()
            default_home.save()

        except:  # noqa
            pass

        cls.root = Page.objects.get(id=1).specific
        cls.home_page = HomePage(
            title="Home", slug="home", hero_text="You can do it", hero_cta="Learn More"
        )
        cls.city_index_page = CityIndexPage(title="cities", slug="cities")

        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)

        # Save and publish Home Page
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        # Add CityIndexPage as child of HomePage
        cls.home_page.add_child(instance=cls.city_index_page)
        cls.city_index_page.save_revision().publish()
        cls.city_index_page.save()

    def test_default_route(self):
        self.assertPageIsRoutable(self.city_index_page)

    def test_editability(self):
        self.assertPageIsEditable(self.city_index_page)

    def test_can_create_city_index_under_home_page(self):
        self.assertCanCreateAt(HomePage, CityIndexPage)

    def test_can_create_city_page_under_cityindexpage(self):
        self.assertCanCreateAt(CityIndexPage, CityPage)

    def test_cannot_create_wrong_children_or_parents_for_city_index_page(self):
        self.assertCanNotCreateAt(CityIndexPage, HomePage)
        self.assertCanNotCreateAt(CityPage, CityIndexPage)

    def test_city_index_page_parent_pages(self):
        self.assertAllowedParentPageTypes(CityIndexPage, {HomePage})

    def test_city_index_page_subpages(self):
        self.assertAllowedSubpageTypes(CityIndexPage, {CityPage})
