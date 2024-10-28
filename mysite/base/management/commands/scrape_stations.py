import csv
import logging
import random
import time

from django.core.management.base import BaseCommand

import requests
from base.scrapers.base import HEADERS
from bs4 import BeautifulSoup

INPUT_CSV = "city_stations.csv"
OUTPUT_CSV = "stations.csv"
BATCH_SIZE = 5

logger = logging.getLogger(__name__)
session = requests.Session()


class Command(BaseCommand):
    """
    Scraper to pull an individual station data.
    """

    def handle(self, **options):
        logger.warn(
            "It is recommended you empty %s file to avoid duplicates\n" % INPUT_CSV
        )
        logger.info("running stations scraper...")

        # 1. Get list of all stations to be scraped
        city_stations = self.read_csv(INPUT_CSV)
        num_stations = len(city_stations)

        logger.info("Total stations to scrape:%s" % num_stations)
        logger.info("Batch Size:%s" % BATCH_SIZE)

        # 2. Now scrape them in batches
        for i in range(1, num_stations, BATCH_SIZE):
            chunk = city_stations[i : i + BATCH_SIZE]
            self.save_stations(chunk=chunk)

        self.stdout.write("All Done ✨🚀")

    def write_csv(self, filename: str = None, data: list = None) -> None:
        """
        Helper method to write a list of tuples to a local csv file.
        """

        with open(filename, "a", newline="") as f:
            writer = csv.writer(
                f,
                delimiter=" ",
                quotechar="|",
                quoting=csv.QUOTE_MINIMAL,
                escapechar="\\",
            )
            for row in data:
                writer.writerow(row)

    @classmethod
    def read_csv(self, filename: str = None) -> list[tuple]:
        """
        Read input csv file that contains list of all stations for each city per row
        """

        with open(filename, newline="") as csv_file:
            city_stations_reader = csv.reader(csv_file, delimiter=" ", quotechar="|")
            city_stations = [tuple(row) for row in city_stations_reader]

        return city_stations

    @classmethod
    def get_station_data(cls, station_url: str = None) -> tuple:
        """
        Scrapes the data for a single bus station
        """
        try:

            response = requests.get(station_url, headers=HEADERS, timeout=10)
            bs = BeautifulSoup(response.text, "html.parser")

        except requests.exceptions.RequestException as e:
            logger.warning(e)
            logger.warning("skipping url:%s" % station_url)
            return ("", "", "")

        name = (
            bs.find("h1")
            .get_text()
            .lstrip("Find cheap bus tickets from ")
            .replace("\xa0", " ")
        )

        try:
            address = bs.find("address").get_text().strip()
            lat_long = bs.find("address").a.attrs["href"].split("query=")[1]

        except AttributeError as e:
            logger.warn(e)
            logger.warn("Address element not found for station:%s" % name)
            address = lat_long = ""

        logger.info("station:%s" % name)

        return name, address, lat_long

    def save_stations(self, chunk: list) -> None:
        stations = []

        for city, station, url in chunk:
            time.sleep(random.randint(1, 3))  # act like human

            url = f"https://busbud.com{url}"
            station_data = self.get_station_data(station_url=url)
            chunk = (city,) + station_data + (url,)
            stations.append(chunk)

        logger.info("writing intermediate csv...\n")

        self.write_csv(OUTPUT_CSV, stations)
