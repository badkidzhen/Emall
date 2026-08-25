from django.contrib import admin

from .models import RewardDistributionRecord, RewardPool, RewardPoolRule

admin.site.register(RewardPool)
admin.site.register(RewardPoolRule)
admin.site.register(RewardDistributionRecord)

