from django.contrib import admin
from .models import ServiceServiceTicket, ServiceAMCContract, ServiceEquipment, PendingComplaints, ServiceAMCCoverageItem
from core.admin import ServiceTicketAdmin, AMCContractAdmin, EquipmentAdmin, PendingComplaintsAdmin, AMCCoverageItemAdmin

admin.site.register(ServiceServiceTicket, ServiceTicketAdmin)
admin.site.register(ServiceAMCContract, AMCContractAdmin)
admin.site.register(ServiceEquipment, EquipmentAdmin)
admin.site.register(PendingComplaints, PendingComplaintsAdmin)
admin.site.register(ServiceAMCCoverageItem, AMCCoverageItemAdmin)
