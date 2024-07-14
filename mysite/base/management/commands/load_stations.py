import csv
import logging

from django.core.management.base import BaseCommand

from wagtail.models import Locale

from locations.models import CityPage, StationPage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Load stations.csv to the database"""

    def handle(self, **options):
        en = Locale.objects.get(language_code="en")

        stations = self.read_stations()

        for city, station, address, lat_long, url in stations:

            seo_title = f"{station} | Bus station in Argentina"
            lat_long = ",".join(x[:12] for x in lat_long.split(","))

            try:
                station_page = StationPage.objects.get(title=station, locale=en)
                logger.info("already exists station:%s" % station)

            except StationPage.DoesNotExist:
                logger.info("loading city:%s" % city)
                city_page = CityPage.objects.get(title=city, locale=en)

                # Create station and add as child to city
                station_page = StationPage(
                    title=station,
                    address=address,
                    lat_long=lat_long,
                    seo_title=seo_title,
                    locale=en,
                )
                city_page.add_child(instance=station_page)
                station_page.save_revision().publish()

        self.stdout.write(
            "Recommendation: Run the fixtree mgmt command to avoid problems 🌳"
        )
        self.stdout.write("All Done 💄✨💫")

    def read_stations(self):
        with open("stations.csv", newline="") as csv_file:
            station_reader = csv.reader(csv_file, delimiter=" ", quotechar="|")
            stations = [tuple(row) for row in station_reader if row]

        return stations
