import asyncio

from django.core.management.base import BaseCommand

from ...scraper import fetch_all_types


class Command(BaseCommand):
    help = "Runs the web scraper"

    def add_arguments(self, parser):
        parser.add_argument("--profile", action="store_true", default=False)

    def handle(self, *args, **options):
        if options.get("profile", False):
            try:
                import yappi
            except ImportError:
                print(
                    "yappi is not installed, please install it to use the --profile option"
                )
                return
            yappi.set_clock_type("CPU")
            with yappi.run():
                self._handle(*args, **options)
            yappi.get_func_stats().save("scraper_run.prof", type="callgrind")
        else:
            self._handle(*args, **options)

    def _handle(self, *args, **options):
        asyncio.run(fetch_all_types())
