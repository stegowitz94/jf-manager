import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
class Command(BaseCommand):
    help = "Wait until the default database is available."
    def handle(self, *args, **options):
        for attempt in range(30):
            try:
                connections["default"].cursor()
                self.stdout.write(self.style.SUCCESS("Database available."))
                return
            except OperationalError:
                self.stdout.write(f"Database unavailable, retry {attempt + 1}/30...")
                time.sleep(2)
        raise OperationalError("Database did not become available in time.")
