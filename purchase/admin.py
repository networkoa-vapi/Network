from django.contrib import admin
from .models import ItemsToPurchase, SupplierPurchaseOrder
from core.admin import ItemsToPurchaseAdmin, SupplierPurchaseOrderAdmin

admin.site.register(ItemsToPurchase, ItemsToPurchaseAdmin)
admin.site.register(SupplierPurchaseOrder, SupplierPurchaseOrderAdmin)
