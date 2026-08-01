from django.contrib import admin
from .models import Project, PurchaseRequisition
from core.admin import ProjectAdmin, PurchaseRequisitionAdmin

admin.site.register(Project, ProjectAdmin)
admin.site.register(PurchaseRequisition, PurchaseRequisitionAdmin)
