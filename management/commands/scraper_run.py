import asyncio
from cProfile import Profile

from django.core.management.base import BaseCommand

from ...scraper import fetch_all_types


class Command(BaseCommand):
    help = "Runs the web scraper"

    def add_arguments(self, parser):
        parser.add_argument("--profile", action="store_true", default=False)

    def handle(self, *args, **options):
        if options.get("profile", False):
            profiler = Profile()
            profiler.runcall(self._handle, *args, **options)
            profiler.dump_stats("scraper_run.prof")
        else:
            self._handle(*args, **options)

    def _handle(self, *args, **options):
        asyncio.run(fetch_all_types())
