import csv
import logging
import random
import time

from django.core.management.base import BaseCommand

import requests
from base.scrapers.base import HEADERS
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X)"
    "AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257"
    "Safari/9537.53",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
    "q=0.9,image/webp,*/*;q=0.8",
}

cities_url = "https://www.busbud.com/en/sitemap/cs/AR"

logger = logging.getLogger(__name__)
session = requests.Session()


class Command(BaseCommand):
    """
    Scraper for Busbud
    """

    @classmethod
    def get_stations(cls, city_url=None) -> list:
        """
        Parses a city url and builds a list of (terminal_name, terminal_url)
        """

        response = requests.get(city_url, headers=HEADERS, timeout=10)
        bs = BeautifulSoup(response.text, "html.parser")

        city = bs.find("h1").get_text().lstrip("Stations in ")
        links = bs.find_all("li", {"class": "suggestion"})
        stations = [(city, link.a.get_text(), link.a.attrs["href"]) for link in links]

        logger.info("city:%s" % city)

        return stations

    def write_csv(self, filename=None, data=None) -> None:
        """
        Helper method to write a list of tuples to a local csv file.
        """

        with open(filename, "w", newline="") as f:
            writer = csv.writer(
                f,
                delimiter=" ",
                quotechar="|",
                quoting=csv.QUOTE_MINIMAL,
                escapechar="\\",
            )
            for row in data:
                writer.writerow(row)

    def handle(self, **options):
        logger.info("running scraper...")

        response = requests.get(cities_url, headers=HEADERS, timeout=10)
        bs = BeautifulSoup(response.text, "html.parser")

        links = bs.find_all("li", {"class": "suggestion"})
        cities = [
            (link.a.get_text().lstrip("Stations in "), link.a.attrs["href"])
            for link in links
        ]

        self.write_csv("cities.csv", cities)
        logger.info("cities.csv saved...")

        # Stations
        stations = []

        for name, url in cities:
            # act like human
            time.sleep(random.randint(1, 3))  # nosec

            city_url = f"https://busbud.com{url}"
            city_stations = self.get_stations(city_url=city_url)
            stations.extend(city_stations)

        self.write_csv(filename="city_stations.csv", data=stations)
        self.stdout.write("All Done ✨🚀")
