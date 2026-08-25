from celery import shared_task

from .services import expire_coupons


@shared_task
def expire_coupons_task(limit=1000):
    return expire_coupons(limit=limit)
