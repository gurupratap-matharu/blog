from unittest import skip

from django.utils import timezone

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, streamfield

from home.models import HomePage
from partners.models import PartnerIndexPage, PartnerPage


class PartnerIndexPageTests(WagtailPageTestCase):
    """
    Test suite for the partner index page.
    """

    template_name = "partners/partner_index_page.html"

    @classmethod
    def setUpTestData(cls):
        cls.root = Page.get_first_root_node()
        cls.home_page = HomePage(
            title="Home", hero_text="You can do it", hero_cta="Learn More"
        )
        cls.partner_index_page = PartnerIndexPage(
            title="Empresas de bus", slug="empresas-de-bus"
        )

        # Build page hierarchy
        cls.root.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        cls.home_page.add_child(instance=cls.partner_index_page)
        cls.partner_index_page.first_published_at = timezone.now()
        cls.partner_index_page.last_published_at = timezone.now()
        cls.partner_index_page.save_revision().publish()
        cls.partner_index_page.save()

    def test_get(self):
        response = self.client.get(self.partner_index_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_default_route(self):
        self.assertPageIsRoutable(self.partner_index_page)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.partner_index_page)

    def test_page_is_previewable(self):
        self.assertPageIsPreviewable(self.partner_index_page)

    def test_editability(self):
        self.assertPageIsEditable(self.partner_index_page)

    def test_can_create_partner_index_under_home_page(self):
        self.assertCanCreateAt(HomePage, PartnerIndexPage)

    def test_can_create_partner_page_under_partnerindexpage(self):
        self.assertCanCreateAt(PartnerIndexPage, PartnerPage)


class PartnerPageTests(WagtailPageTestCase):
    """
    Test suite for the partner page.
    """

    template_name = "partners/partner_page.html"

    @classmethod
    def setUpTestData(cls):
        cls.root = Page.get_first_root_node()
        cls.home_page = HomePage(
            title="Home",
            hero_text="You can do it",
            hero_cta="Learn More",
        )
        cls.partner_index_page = PartnerIndexPage(
            title="Empresas de bus", slug="empresas-de-bus"
        )
        cls.partner_page = PartnerPage(title="Cata International", slug="cata")

        # Build page hierarchy
        cls.root.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        cls.home_page.add_child(instance=cls.partner_index_page)
        cls.partner_index_page.save_revision().publish()
        cls.partner_index_page.save()

        # Add PartnerPage as child of PartnerIndexPage
        cls.partner_index_page.add_child(instance=cls.partner_page)
        cls.partner_page.first_published_at = timezone.now()
        cls.partner_page.last_published_at = timezone.now()
        cls.partner_page.save_revision().publish()
        cls.partner_page.save()

        cls.post_data = nested_form_data(
            {
                "title": "Cata International",
                "body": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "destinations": streamfield(
                    [("text", "Lorem ipsum dolor sit amet")]
                ),
                "info": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "routes": streamfield(
                    [("text", "Lorem ipsum dolor sit amet")]
                ),
                "faq": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "links": streamfield([("text", "Lorem ipsum dolor sit amet")]),
                "contact": streamfield(
                    [("text", "Lorem ipsum dolor sit amet")]
                ),
                # TODO: this is not correct
                "ratings": streamfield(
                    [("text", "Lorem ipsum dolor sit amet")]
                ),
            }
        )

    def test_get(self):
        response = self.client.get(self.partner_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertNotContains(response, "Hi I should not be on this page")

    def test_default_route(self):
        self.assertPageIsRoutable(self.partner_page)

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.partner_page)

    @skip("Not sure how to correctly pass post data (ratings)")
    def test_page_is_previewable(self):
        self.assertPageIsPreviewable(
            self.partner_page, post_data=self.post_data
        )

    def test_editability(self):
        self.assertPageIsEditable(
            self.partner_index_page, post_data=self.post_data
        )

    def test_can_create_partner_page_under_partnerindex_page(self):
        self.assertCanCreateAt(PartnerIndexPage, PartnerPage)
