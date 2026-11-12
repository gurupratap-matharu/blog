import random
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta as td
from timeit import default_timer as timer

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_time

import requests
from bs4 import BeautifulSoup, Tag

from trips.models import Company, Route, Trip


HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X)"
    "AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257"
    "Safari/9537.53",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

session = requests.Session()


class Command(BaseCommand):
    help = "Pull fresh data for our routes from the outside world."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("route_ids", nargs="*", type=int)
        parser.add_argument("--limit", default="10", type=int)

    def handle(self, *args, **options) -> str:
        self.route_ids = options["route_ids"]
        limit = options["limit"]

        start = timer()
        qs = Route.objects.filter(is_active=True)

        if self.route_ids:
            qs = qs.filter(id__in=self.route_ids)

        qs = qs.select_related("origin", "destination").order_by("updated")
        qs = qs[:limit]

        self.success("using red strategy...")
        self.stdout.write(f"limiting to {limit} routes...")

        items = qs.count()
        for i, obj in enumerate(qs, start=1):
            self.pull_red(obj)

            is_last_cycle = i == items
            if not is_last_cycle:
                self.wait()

        end = timer()
        out = f"Took {(end - start):.2f} seconds."
        self.success(out)
        return f"Done. {out}"

    def pull_red(self, obj) -> bool:
        # Parse all trips first
        soup = self.fetch(obj)
        cards = soup.find_all(class_="nC-N2W_card")
        trips = [self.parse_card(obj, card) for card in cards]

        if not trips:
            # no search results
            return False

        # Build route metadata from trips - they don't provide
        num_companies = len({t.get("company") for t in trips})

        first_departure = min([t.get("departure") for t in trips]).time()
        last_departure = max([t.get("departure") for t in trips]).time()
        num_departures = len(trips)

        # TODO: Check to add price_b, price_c in the calculation
        min_price = min(t.get("price_a") for t in trips)
        avg_price = sum(t.get("price_a") for t in trips) / num_departures

        min_duration = min(t.get("duration") for t in trips)
        avg_duration = sum([t.get("duration") for t in trips], td()) / num_departures

        self.stdout.write(f"min price:{min_price} avg price:{avg_price}")
        self.stdout.write(f"first departure:{first_departure} last departure:{last_departure}")
        self.stdout.write(f"avg duration:{avg_duration} min duration:{min_duration}")
        self.stdout.write(f"num departures:{num_departures} num companies:{num_companies}")

        obj.num_companies = num_companies
        obj.first_departure = first_departure
        obj.last_departure = last_departure
        obj.num_departures = num_departures
        obj.min_price = min_price
        obj.avg_price = avg_price
        obj.avg_duration = avg_duration
        obj.min_duration = min_duration
        obj.save()

        with transaction.atomic():
            # Remove all previous Auto trips - revise this later
            obj.trips.filter(strategy=Trip.Strategy.AUTO).delete()

            # Create trips
            count = 0
            for trip in trips:
                _, created = Trip.objects.get_or_create(route=obj, **trip)
                count += 1 if created else 0

        self.stdout.write(f"trips created:{count}")

        return True

    def fetch(self, obj) -> BeautifulSoup:
        self.success(f"pulling route:{obj}")
        url = obj.get_red_url()

        try:
            r = session.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            self.error("Http Error:", errh.response.text)
        except requests.exceptions.ConnectionError as errc:
            self.error("Error Connecting:", errc.response.text)
        except requests.exceptions.Timeout as errt:
            self.error("Timeout Error:", errt.response.text)
        except requests.exceptions.RequestException as err:
            self.error("Oops: Something Else", err.response.text)

        return BeautifulSoup(r.text, "html.parser")

    def parse_card(self, obj: Route, tag: Tag) -> dict:
        """Parse each trip from Red search results"""

        departure = self.clean_red_departure(obj, tag)
        arrival = self.clean_red_arrival(obj, tag)

        if arrival < departure:
            # If arrival < departure it means trip reached the next day
            # increment day by 1
            arrival = arrival + td(days=1)

        trip = {
            "company": self.clean_red_company(tag),
            "departure": departure,
            "arrival": arrival,
            "duration": self.clean_red_duration(tag),
            "category_a": self.clean_red_category(tag, row=0),
            "price_a": self.clean_red_price(tag, row=0),
        }

        cat_b = self.clean_red_category(tag, row=1)
        cat_c = self.clean_red_category(tag, row=2)

        price_b = self.clean_red_price(tag, row=1)
        price_c = self.clean_red_price(tag, row=2)

        if cat_b and price_b:
            trip["category_b"] = cat_b
            trip["price_b"] = price_b

        if cat_c and price_c:
            trip["category_c"] = cat_c
            trip["price_c"] = price_c

        return trip

    def clean_red_departure(self, obj: Route, tag: Tag) -> datetime:
        txt = tag.find(attrs={"data-testid": "service-departure-time"}).get_text().strip().rstrip("hs")
        return self.parse_dt(obj, txt)

    def clean_red_arrival(self, obj: Route, tag: Tag) -> datetime:
        txt = tag.find(attrs={"data-testid": "service-arrival-time"}).get_text().strip().rstrip("hs")
        return self.parse_dt(obj, txt)

    def clean_red_company(self, tag: Tag) -> Company:
        red_code = tag.find(attrs={"data-testid": "service-company"}).attrs.get("alt").strip()
        try:
            c = Company.objects.get(red_code=red_code)
        except Company.DoesNotExist as e:
            out = f"Company with red_code:{red_code} does not exist!"
            self.error(out)
            e.add_note(out)
            raise

        return c

    def clean_red_duration(self, tag: Tag) -> td:
        """Converts 4h -> td(hours=4), 6h 15m -> td(hours=6, minutes=15)"""

        txt = tag.find(attrs={"data-testid": "service-duration"}).get_text().strip()
        txt = txt.replace("h", "").replace("m", "").split(" ")
        lst = [int(x) for x in txt]
        hours, *mins = lst
        minutes = mins[0] if mins else 0
        return td(hours=hours, minutes=minutes)

    def clean_red_category(self, tag: Tag, row: int) -> Trip.Category:
        div = tag.find(attrs={"data-testid": f"service-quality-row-{row}"})

        if not div:
            return

        cat = div.find(class_="nC-N2W_qualityName").get_text().strip().lower()
        map = {
            "cama suite": Trip.Category.CAMASUITE,
            "cama ejecutivo": Trip.Category.CAMAEJECUTIVO,
            "cama": Trip.Category.CAMA,
            "semicama": Trip.Category.SEMICAMA,
            "comun": Trip.Category.COMMON,
        }
        return map.get(cat, Trip.Category.SEMICAMA)

    def clean_red_price(self, tag: Tag, row: int) -> str:
        """Convertes 110.000 -> 11000"""
        div = tag.find(attrs={"data-testid": f"service-quality-row-{row}"})
        if not div:
            return

        # this gives for ex: 'ARS 101.500'
        txt = div.find(attrs={"data-testid": f"service-quality-amount-{row}"}).get_text().strip()
        txt = txt.lstrip("ARS").strip()
        txt = txt.replace(".", "")
        return int(txt)

    def parse_dt(self, obj: Route, time: str) -> datetime:
        # converts '05:15' -> aware datetime
        t = parse_time(time)
        dt = obj.next_departure().replace(
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            microsecond=t.microsecond,
        )
        return dt

    def wait(self) -> None:
        # don't wait if manually updating single route via admin
        if len(self.route_ids) == 1:
            return

        secs = random.choice([2, 3, 4, 5])
        self.error(f"waiting {secs} secs...")
        time.sleep(secs)

    def success(self, msg) -> None:
        self.stdout.write(self.style.SUCCESS(msg))

    def error(self, msg) -> None:
        self.stdout.write(self.style.ERROR(msg))
