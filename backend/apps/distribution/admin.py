from django.contrib import admin

from .models import CommissionRecord, DistributionConfigModel, UserTeamStat

admin.site.register(UserTeamStat)
admin.site.register(DistributionConfigModel)
admin.site.register(CommissionRecord)

