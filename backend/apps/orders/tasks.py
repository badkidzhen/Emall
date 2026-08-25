from celery import shared_task

from .services import close_expired_pending_orders


@shared_task
def close_expired_pending_orders_task(timeout_minutes=None, limit=100):
    return close_expired_pending_orders(timeout_minutes=timeout_minutes, limit=limit)

