from django.contrib import admin

from .models import FundFlow, Wallet, WithdrawApplication

admin.site.register(Wallet)
admin.site.register(FundFlow)
admin.site.register(WithdrawApplication)
