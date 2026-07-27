from django.contrib import admin
from .models import InventoryDivision, InventoryProduct, InventoryProductCategory, InventoryProductSubCategory, InventoryProductDocument
from core.admin import DivisionAdmin, ProductAdmin, ProductCategoryAdmin, ProductSubCategoryAdmin, ProductDocumentAdmin

admin.site.register(InventoryDivision, DivisionAdmin)
admin.site.register(InventoryProduct, ProductAdmin)
admin.site.register(InventoryProductCategory, ProductCategoryAdmin)
admin.site.register(InventoryProductSubCategory, ProductSubCategoryAdmin)
admin.site.register(InventoryProductDocument, ProductDocumentAdmin)
