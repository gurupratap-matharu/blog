import hashlib
import json
import random
import time
from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

import requests
from bs4 import BeautifulSoup


BASE_DIR = Path.home() / "Downloads" / "cdp"
FAILED_LOG = BASE_DIR / "failed_urls.txt"

OUTPUT_DIR = BASE_DIR / "saved_pages"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DUMP = BASE_DIR / "status.json"

URL_LIST = "urls.txt"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X)"
    "AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257"
    "Safari/9537.53",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
    "q=0.9,image/webp,*/*;q=0.8",
}


class Command(BaseCommand):
    """
    Scraper for CDP
    """

    help = "Pulls in latest data from CDP website"

    def handle(self, *args, **options):

        self.stdout.write("initialising scraper...")

        urls = self.read_urls()
        data = self.read_json()

        for i, url in enumerate(urls, 1):
            self.stdout.write(f"\n[{i}/{len(urls)}] Processing: {url}")

            key = self.url_to_dict_key(url)

            if key in data:
                self.stdout.write(f"[SKIP] Already exists: {url}")
                continue

            # 1. Extract and parse data into dict
            url_data = self.extract_url(url=url)

            # 2. Store data in correct key of dict
            data[key] = url_data

            # 3. Save data after each url
            self.save_to_json(data=data)

            # 4. Act like human
            time.sleep(random.randint(1, 5))

        self.stdout.write(self.style.SUCCESS("All done"))

    def extract_url(self, url):
        filename = self.url_to_filename(url)
        filepath = OUTPUT_DIR / filename
        data = dict()

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"[OK] Saved: {filename}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"[ERROR] Failed to fetch {url}: {e}")
            )
            with open(FAILED_LOG, "a") as f:
                f.write(url + "\n")

            return

        else:
            bs = BeautifulSoup(response.text, "html.parser")

            parts = url.split("/")
            data["origin_code"], data["destination_code"] = (
                parts[-2],
                parts[-1],
            )

            for el in bs.find("footer").find_all("input"):
                name = el.attrs.get("name")
                value = el.attrs.get("value")

                if name not in ("hidListaBusTrip", "hidUrlVuelta"):
                    key = name.lstrip("hid")
                    data[key] = value

            return data

    def url_to_filename(self, url):
        """Create a unique, readable filename from the URL."""

        parsed = urlparse(url)
        slug = parsed.path.strip("/").replace("/", "-")
        hash_suffix = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{slug}-{hash_suffix}.html"

    def url_to_dict_key(self, url):
        """Build a key to store in json representing a url"""

        url_parts = url.split("/")
        origin, destination = url_parts[-2], url_parts[-1]

        return f"{origin}:{destination}"

    def read_urls(self):
        with open(URL_LIST, "r") as f:
            urls = [line.strip() for line in f if line.strip()]

        return urls

    def read_json(self):
        try:
            with open(OUTPUT_DUMP, "r") as f:
                data = json.load(f)

        except FileNotFoundError:
            self.stdout.write(
                "Could not find json so starting with empty dict"
            )
            data = dict()

        return data

    def save_to_json(self, data):

        with open(OUTPUT_DUMP, "w", encoding="utf-8") as f_json:
            json.dump(data, f_json, ensure_ascii=False, indent=4)
