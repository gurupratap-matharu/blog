from argparse import ArgumentParser
from timeit import default_timer as timer

from django.core.management import call_command
from django.core.management.base import BaseCommand

from trips.models import Route


class Command(BaseCommand):
    help = "Pull fresh data for our routes based on their own preference"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("route_ids", nargs="*", type=int)
        parser.add_argument("--limit", default="10", type=int)

    def handle(self, *args, **options) -> str:
        route_ids = options["route_ids"]
        limit = options["limit"]

        start = timer()
        qs = Route.objects.filter(is_active=True)
        if route_ids:
            qs = qs.filter(id__in=route_ids)
        qs = qs.select_related("origin", "destination").order_by("updated")

        blue_qs = qs.filter(pull_preference=Route.PullPreference.BLUE)
        red_qs = qs.filter(pull_preference=Route.PullPreference.RED)

        blue_ids = [obj.id for obj in blue_qs]
        red_ids = [obj.id for obj in red_qs]

        # TODO: Call both of these together in a thread. possible?
        if blue_ids:
            out = call_command("pull_blue", blue_ids, limit=limit)

        if red_ids:
            out = call_command("pull_red", red_ids, limit=limit)

        end = timer()
        out = f"Took {(end - start):.2f} seconds."
        self.success(out)
        return f"Done. {out}"

    def success(self, msg) -> None:
        self.stdout.write(self.style.SUCCESS(msg))
