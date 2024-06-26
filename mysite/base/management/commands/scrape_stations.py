import csv
import logging
import random
import time
from urllib.request import urlopen

from django.core.management.base import BaseCommand

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Busbud Scraper")

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X)"
    "AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257"
    "Safari/9537.53",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
    "q=0.9,image/webp,*/*;q=0.8",
}

cities_url = "https://www.busbud.com/en/sitemap/cs/AR"


class Command(BaseCommand):
    """
    Scraper for Busbud
    """

    @classmethod
    def get_station_data(cls, station_url=None) -> tuple:
        """
        Scrapes the data for a single bus station.
        """

        html = urlopen(station_url)
        bs = BeautifulSoup(html, "html.parser")
        name = (
            bs.find("h1")
            .get_text()
            .lstrip("Find cheap bus tickets from ")
            .replace("\xa0", " ")
        )
        address = bs.find("address").get_text().strip()
        lat_long = bs.find("address").a.attrs["href"].split("query=")[1]

        logger.info("station:%s" % name)

        return name, address, lat_long

    @classmethod
    def get_stations(cls, city_url=None) -> list:
        """
        Parses a city url and builds a list of (terminal_name, terminal_url)
        """

        html = urlopen(city_url)
        bs = BeautifulSoup(html, "html.parser")

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
                f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            for row in data:
                writer.writerow(row)

    def handle(self, **options):
        logger.info("running scraper...")

        html = urlopen(cities_url)  # nosec
        bs = BeautifulSoup(html, "html.parser")
        links = bs.find_all("li", {"class": "suggestion"})
        cities = [
            (link.a.get_text().lstrip("Stations in "), link.a.attrs["href"])
            for link in links
        ]

        self.write_csv("cities.csv", cities)
        logger.info("cities.csv saved...")

        # Station Scraping Logic

        stations = []

        for name, url in random.sample(cities, k=5):
            # act like human
            time.sleep(random.randint(1, 5))  # nosec

            city_url = f"https://busbud.com{url}"
            city_stations = self.get_stations(city_url=city_url)
            stations.extend(city_stations)

        logger.info("scraping stations...")

        stations_data = []

        for city, station, url in stations:
            time.sleep(random.randint(1, 5))

            station_url = f"https://busbud.com{url}"
            station_data = self.get_station_data(station_url=station_url)
            chunk = (city,) + station_data + (station_url,)
            stations_data.append(chunk)

        self.write_csv("stations.csv", stations_data)
        logger.info("stations.csv saved...")

        self.stdout.write("All Done ✨🚀")
