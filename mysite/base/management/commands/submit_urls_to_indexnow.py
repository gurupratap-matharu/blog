from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from bs4 import BeautifulSoup


class Command(BaseCommand):
    """
    Command that submits all the urls of our sitemap to index now via post request.
    """

    SITEMAP_URL = f"{settings.BASE_URI}/sitemap.xml"
    INDEXNOW_URL = "https://api.indexnow.org/IndexNow"

    def handle(self, *args, **kwargs):
        self.stdout.write("fetching sitemap...")

        r = requests.get(self.SITEMAP_URL, timeout=10)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, features="xml")
        urls = [loc.text for loc in soup.find_all("loc")]

        self.submit_urls(urls=urls)
        return "All Done"

    def submit_urls(self, urls):
        payload = {
            "host": f"{settings.BASE_URI}",
            "key": settings.INDEXNOW_KEY,
            "keyLocation": f"{settings.BASE_URI}/{settings.INDEXNOW_KEY}.txt",
            "urlList": urls,
        }

        headers = {"Content-type": "application/json", "charset": "utf-8", "Host": "api.indexnow.org"}

        try:
            r = requests.post(
                url=self.INDEXNOW_URL,
                headers=headers,
                json=payload,
                timeout=10,
            )
            r.raise_for_status()

        except requests.exceptions.RequestException as e:
            msg = "Error submitting to IndexNow:%s", e
            self.error(msg)
        else:
            self.success(f"Successfully submitted {len(urls)} URLs to IndexNow.")

    def success(self, msg) -> None:
        self.stdout.write(self.style.SUCCESS(msg))

    def error(self, msg) -> None:
        self.stdout.write(self.style.ERROR(msg))
