from celery import shared_task

from .services import calculate_order_commission as calculate_order_commission_service
from .services import settle_due_commissions, sync_user_team_stat as sync_user_team_stat_service


@shared_task
def calculate_order_commission(order_id):
    records = calculate_order_commission_service(order_id)
    return {"order_id": order_id, "created_or_existing": len(records)}


@shared_task
def sync_team_stat(user_id=None):
    if user_id is None:
        return {"user_id": None, "status": "skipped"}
    stat = sync_user_team_stat_service(user_id)
    return {"user_id": stat.user_id, "team_count": stat.team_count}


@shared_task
def settle_due_commissions_task(limit=500):
    return settle_due_commissions(limit=limit)
