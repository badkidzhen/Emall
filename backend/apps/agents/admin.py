from django.contrib import admin

from .models import CityAgent, CityAgentApplication

admin.site.register(CityAgentApplication)
admin.site.register(CityAgent)

