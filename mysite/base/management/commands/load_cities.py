import csv
import logging

from django.core.management.base import BaseCommand

from wagtail.models import Locale

from locations.models import CityIndexPage, CityPage

from base.models import Country


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Load cities.csv to the database"""

    def handle(self, **options):
        en = Locale.objects.get(language_code="en")
        argentina = Country.objects.get(title="Argentina")

        city_index = CityIndexPage.objects.get(locale=en)

        cities = self.read_cities()

        for city, url in cities:
            seo_title = f"{city} | City in Argentina"

            try:
                city_page = CityPage.objects.get(title=city, locale=en)
                logger.info("already exists city:%s" % city)

            except CityPage.DoesNotExist:
                city_page = CityPage(
                    title=city, country=argentina, seo_title=seo_title
                )
                city_index.add_child(instance=city_page)
                city_page.save_revision().publish()

                logger.info("created new city:%s" % city)

        self.stdout.write(
            "Recommendation: Run the fixtree mgmt command to avoid problems 🌳"
        )
        self.stdout.write("All Done 💄✨💫")

    def read_cities(self):
        with open("cities.csv", newline="") as csv_file:
            city_reader = csv.reader(csv_file, delimiter=" ", quotechar="|")
            cities = [tuple(row) for row in city_reader]

        return cities
