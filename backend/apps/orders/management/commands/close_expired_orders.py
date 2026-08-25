from django.conf import settings
from django.core.management.base import BaseCommand

from apps.orders.services import close_expired_pending_orders


class Command(BaseCommand):
    help = "Close pending payment orders that exceeded the payment timeout."

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
            default=settings.ORDER_PAYMENT_TIMEOUT_MINUTES,
            help="Payment timeout in minutes.",
        )
        parser.add_argument("--limit", type=int, default=100, help="Maximum orders to close.")

    def handle(self, *args, **options):
        result = close_expired_pending_orders(timeout_minutes=options["minutes"], limit=options["limit"])
        self.stdout.write(self.style.SUCCESS(f"Closed {result['closed_count']} expired orders."))
        for item in result["failed"]:
            self.stdout.write(self.style.WARNING(f"Failed order {item['order_id']}: {item['error']}"))
