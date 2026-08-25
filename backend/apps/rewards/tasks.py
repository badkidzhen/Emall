from celery import shared_task

from .services import distribute_pool


@shared_task
def distribute_reward_pool(pool_id):
    records = distribute_pool(pool_id)
    return {"pool_id": pool_id, "record_count": len(records)}
