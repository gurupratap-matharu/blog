import random
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta as td
from timeit import default_timer as timer

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import requests

from trips.models import Company, Route, Trip


headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "text/plain",
    "Origin": f"{settings.BLUE_BASE_URL}",
    "Referer": f"{settings.BLUE_BASE_URL}/login",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
}

session = requests.Session()
session.headers.update(headers)


class Command(BaseCommand):
    help = "Pull fresh data from the blue world."

    access_token = None
    auth_cookie = None

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("route_ids", nargs="*", type=int)
        parser.add_argument("--limit", default="10", type=int)

    def handle(self, **options):
        self.route_ids = options["route_ids"]
        limit = options["limit"]

        start = timer()

        qs = Route.objects.filter(is_active=True)

        if self.route_ids:
            qs = qs.filter(id__in=self.route_ids)

        qs = qs.select_related("origin", "destination").order_by("updated")
        qs = qs[:limit]

        self.success("using blue strategy...")
        self.stdout.write(f"limiting to {limit} routes...")

        # Get authorised first - one time for all routes
        self.get_public_key()
        self.authorize()

        items = qs.count()
        for i, obj in enumerate(qs, start=1):
            self.pull_blue(obj)

            is_last_cycle = i == items
            if not is_last_cycle:
                self.wait()

        end = timer()
        out = f"Took {(end - start):.2f} seconds."
        self.success(out)
        return f"Done. {out}"

    def pull_blue(self, obj: Route) -> None:
        data = self.fetch(obj)
        raw_trips = data.get("Trips").get("oneWay")
        # no search results
        if not raw_trips:
            return

        trips = [self.parse_trip(x) for x in raw_trips]

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

    def fetch(self, obj: Route) -> dict:
        self.success(f"pulling route:{obj}")

        referer_url = obj.get_blue_url()
        session.headers.update({"Referer": referer_url})

        url = f"{settings.BLUE_BASE_URL}/back/api/trips"
        payload = self.get_payload(obj)

        try:
            r = session.post(url, json=payload, timeout=10)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            self.error("Http Error:", errh.response.text)
        except requests.exceptions.ConnectionError as errc:
            self.error("Error Connecting:", errc.response.text)
        except requests.exceptions.Timeout as errt:
            self.error("Timeout Error:", errt.response.text)
        except requests.exceptions.RequestException as err:
            self.error("Oops: Something Else", err.response.text)

        return r.json()

    def parse_trip(self, chunk: dict) -> dict:
        # convert blue to our format

        trip = {
            "company": self.clean_blue_company(chunk),
            "departure": self.clean_blue_departure(chunk),
            "arrival": self.clean_blue_arrival(chunk),
            "duration": self.clean_blue_duration(chunk),
            "category_a": self.clean_blue_category(chunk, row=0),
            "price_a": self.clean_blue_price(chunk, row=0),
        }
        cat_b = self.clean_blue_category(chunk, row=1)
        price_b = self.clean_blue_price(chunk, row=1)

        if cat_b and price_b:
            trip["category_b"] = cat_b
            trip["price_b"] = price_b

        return trip

    def clean_blue_company(self, chunk: dict) -> Company:
        blue_code = chunk.get("companyName")

        name_overrides = {"El Pulqui LTO": "El Pulqui"}
        blue_code = name_overrides.get(blue_code, blue_code)

        try:
            c = Company.objects.get(blue_code=blue_code)
        except Company.DoesNotExist as e:
            out = f"Company with blue_code:{blue_code} does not exist!"
            self.error(out)
            e.add_note(out)
            raise
        return c

    def clean_blue_departure(self, chunk: dict) -> datetime:
        return parse_datetime(chunk.get("departure"))

    def clean_blue_arrival(self, chunk: dict) -> datetime:
        return parse_datetime(chunk.get("arrive"))

    def clean_blue_duration(self, chunk: dict) -> td:
        txt = chunk.get("duration", "")
        txt = txt.split(":")
        hours, minutes = [int(x) for x in txt]
        return td(hours=hours, minutes=minutes)

    def clean_blue_category(self, chunk: dict, row: int) -> Trip.Category:
        try:
            fares = chunk.get("servicesGroupedShort").get("faresInfo")
            # for single fares this is a dict
            if isinstance(fares, dict):
                fares = [fares]
            cat = fares[row].get("shortName").lower()
        except IndexError:
            return

        map = {
            "cama suite": Trip.Category.CAMASUITE,
            "cama ejecutivo": Trip.Category.CAMAEJECUTIVO,
            "cama": Trip.Category.CAMA,
            "semicama": Trip.Category.SEMICAMA,
            "comun": Trip.Category.COMMON,
        }
        return map.get(cat, Trip.Category.SEMICAMA)

    def clean_blue_price(self, chunk: dict, row: int) -> int:
        try:
            fares = chunk.get("servicesGroupedShort").get("faresInfo")
            # for single fares this is a dict
            if isinstance(fares, dict):
                fares = [fares]
            price = fares[row].get("price")
        except IndexError:
            return
        return round(price)

    def get_public_key(self):
        self.stdout.write("fetching key...")

        date = timezone.now().isoformat(timespec="seconds")
        url = f"{settings.BLUE_BASE_URL}/back/key?date={date}"
        r = session.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        self.public_key = data["publicKey"]
        self.client_id = data["client"]
        self.agent = data["agent"]

        return data

    def authorize(self):
        self.stdout.write("authorizing...")
        payload = {
            "Authorization": self.public_key,
            "clientId": self.client_id,
            "Host": "localhost",
        }

        url = f"{settings.BLUE_BASE_URL}/back/api/authorize"
        r = session.post(url, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()

        self.access_token = data["access_token"]
        self.auth_cookie = data["cookie"]

        return data

    def get_payload(self, obj: Route) -> dict:
        departure = obj.next_departure().strftime("%Y-%m-%d")
        payload = {
            "Authorization": self.access_token,
            "auth_cookie": self.auth_cookie,
            "data": {
                "tripDTO": {
                    "tipoBoleto": "NORMAL",
                    "origen": obj.origin.blue_code,
                    "destino": obj.destination.blue_code,
                    "fechaIda": departure,
                    "pax": "1|0",
                }
            },
        }
        return payload

    def wait(self) -> None:
        # don't wait when updating one route via admin
        if len(self.route_ids) == 1:
            return

        secs = random.choice([2, 3, 4, 5])
        self.error(f"waiting {secs} secs...")
        time.sleep(secs)

    def success(self, msg) -> None:
        self.stdout.write(self.style.SUCCESS(msg))

    def error(self, msg) -> None:
        self.stdout.write(self.style.ERROR(msg))
