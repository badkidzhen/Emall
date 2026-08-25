from django.contrib.auth import get_user_model
from django.db import transaction

from .models import CityAgent, CityAgentApplication


class AgentError(ValueError):
    pass


def approve_application(application_id, commission_rate=0, remark=""):
    User = get_user_model()
    with transaction.atomic():
        application = CityAgentApplication.objects.select_for_update().select_related("user").get(pk=application_id)
        if application.status != CityAgentApplication.Status.PENDING:
            raise AgentError("Only pending applications can be approved.")
        agent, _ = CityAgent.objects.update_or_create(
            level=application.level,
            region_code=application.region_code,
            defaults={
                "user": application.user,
                "region_name": application.region_name,
                "commission_rate": commission_rate,
                "enabled": True,
            },
        )
        application.status = CityAgentApplication.Status.APPROVED
        application.audit_remark = remark
        application.save(update_fields=["status", "audit_remark", "updated_at"])
        application.user.role = User.Role.CITY_AGENT
        application.user.city_agent_level = application.level
        application.user.city_code = application.region_code
        application.user.save(update_fields=["role", "city_agent_level", "city_code"])
    return agent


def reject_application(application_id, remark=""):
    with transaction.atomic():
        application = CityAgentApplication.objects.select_for_update().get(pk=application_id)
        if application.status != CityAgentApplication.Status.PENDING:
            raise AgentError("Only pending applications can be rejected.")
        application.status = CityAgentApplication.Status.REJECTED
        application.audit_remark = remark
        application.save(update_fields=["status", "audit_remark", "updated_at"])
    return application
