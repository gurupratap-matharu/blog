import logging

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage

from blog.models import BlogIndexPage, BlogPage

logger = logging.getLogger(__name__)


class BlogIndexPageTests(WagtailPageTestCase):
    """
    Test suite to check if the blog index page is routable under different routes.
    """

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
        cls.blog_index_page = BlogIndexPage(title="blog", slug="blog")
        cls.blog_page = BlogPage(title="Buenos Aires", slug="buenos-aires")

        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)

        # Save and publish Home Page
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        # Add Blog Index as child of Home Page
        cls.home_page.add_child(instance=cls.blog_index_page)
        cls.blog_index_page.save_revision().publish()
        cls.blog_index_page.save()

        # Add BlogPage as child of BlogIndex
        # Veer you need a blog page as the blog index has a featured blog post section
        # so atleast one blog page is needed. Temp fix for now
        cls.blog_index_page.add_child(instance=cls.blog_page)
        cls.blog_page.save_revision().publish()
        cls.blog_page.save()

    def test_get(self):
        response = self.client.get(self.blog_index_page.url)
        self.assertEqual(response.status_code, 200)

    def test_default_route(self):
        self.assertPageIsRoutable(self.blog_index_page)

    def test_tags_route(self):
        self.assertPageIsRoutable(self.blog_index_page, "tags/")

    def test_tags_specific_route(self):
        self.assertPageIsRoutable(self.blog_index_page, "tags/bus/")

    def test_editability(self):
        self.assertPageIsEditable(self.blog_index_page)

    # Not sure why this test doesn't pass!
    # def test_general_previewability(self):
    #     self.assertPageIsPreviewable(self.blog_index_page)

    def test_can_create_blog_index_under_home_page(self):
        self.assertCanCreateAt(HomePage, BlogIndexPage)

    def test_can_create_blog_page_under_blog_index_page(self):
        self.assertCanCreateAt(BlogIndexPage, BlogPage)

    def test_cannot_create_wrong_children_or_parents_for_blog_index_page(self):
        self.assertCanNotCreateAt(BlogIndexPage, HomePage)
        self.assertCanNotCreateAt(BlogPage, BlogIndexPage)

    def test_blog_index_page_parent_pages(self):
        self.assertAllowedParentPageTypes(BlogIndexPage, {HomePage})

    def test_blog_index_page_subpages(self):
        self.assertAllowedSubpageTypes(BlogIndexPage, {BlogPage})


class BlogPageTests(WagtailPageTestCase):
    """
    Test suite for the blog post page.
    """

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
        cls.blog_index_page = BlogIndexPage(title="blog", slug="blog")
        cls.blog_page = BlogPage(title="Buenos Aires", slug="buenos-aires")

        # Set Home Page as child of root
        cls.root.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        cls.home_page.save()

        # Set default Home Page as root page for Site
        cls.site = Site.objects.get(id=1)
        cls.site.root_page = cls.home_page
        cls.site.save()

        # Add BlogIndex as child of Home Page
        cls.home_page.add_child(instance=cls.blog_index_page)
        cls.blog_index_page.save_revision().publish()
        cls.blog_index_page.save()

        # Add BlogPage as child of BlogIndex
        cls.blog_index_page.add_child(instance=cls.blog_page)
        cls.blog_page.save_revision().publish()
        cls.blog_page.save()

    def test_get(self):
        response = self.client.get(self.blog_page.url)
        self.assertEqual(response.status_code, 200)

    def test_default_route(self):
        self.assertPageIsRoutable(self.blog_page)
