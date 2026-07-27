from django.contrib import admin
from .models import ServiceServiceTicket, ServiceAMCContract
from core.admin import ServiceTicketAdmin, AMCContractAdmin

admin.site.register(ServiceServiceTicket, ServiceTicketAdmin)
admin.site.register(ServiceAMCContract, AMCContractAdmin)
