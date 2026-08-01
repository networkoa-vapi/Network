from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    StoreGodown, StoreStockCategory, StoreStockSubCategory, StoreStockItem, StoreStockTransaction,
    PurchaseInward, MaterialIssue, ItemsToIssue,
)
from core.admin import GodownAdmin, StockCategoryAdmin, StockSubCategoryAdmin, StockItemAdmin, StockTransactionAdmin, ItemsToIssueAdmin

admin.site.register(StoreGodown, GodownAdmin)
admin.site.register(StoreStockCategory, StockCategoryAdmin)
admin.site.register(StoreStockSubCategory, StockSubCategoryAdmin)
admin.site.register(StoreStockItem, StockItemAdmin)
admin.site.register(StoreStockTransaction, StockTransactionAdmin)


class PurchaseInwardAdmin(ImportExportModelAdmin):
    list_display = ('voucher_number', 'stock_item', 'godown', 'quantity', 'transaction_date', 'handled_by', 'company')
    list_filter = ('company', 'godown', 'transaction_date')
    search_fields = ('voucher_number', 'stock_item__name', 'stock_item__item_code')
    readonly_fields = ('voucher_number',)
    fieldsets = (
        ('Purchase / Inward Details', {
            'fields': ('company', 'voucher_number', 'stock_item', 'godown', 'quantity'),
            'description': "Record material received into a Godown (from a purchase, or any other inward stock)."
        }),
        ('Notes', {
            'fields': ('handled_by', 'remarks')
        }),
    )

admin.site.register(PurchaseInward, PurchaseInwardAdmin)


class MaterialIssueAdmin(ImportExportModelAdmin):
    list_display = ('voucher_number', 'stock_item', 'godown', 'quantity', 'sales_order', 'party_type', 'transaction_date', 'company')
    list_filter = ('company', 'godown', 'sales_order', 'party_type', 'transaction_date')
    search_fields = ('voucher_number', 'stock_item__name', 'stock_item__item_code', 'party_name')
    readonly_fields = ('voucher_number',)
    fieldsets = (
        ('Issue Details', {
            'fields': ('company', 'voucher_number', 'stock_item', 'godown', 'quantity'),
            'description': "Issue any stock item - Sales Goods, Tools, Capital Goods, Spare Parts, etc. - out of a Godown."
        }),
        ('Project', {
            'fields': ('sales_order',),
            'description': "Link to the customer project this material is issued for, so it can be tracked and billed back to the party."
        }),
        ('Issued To', {
            'fields': ('party_type', 'issued_to_employee', 'issued_to_customer', 'party_name')
        }),
        ('Notes', {
            'fields': ('handled_by', 'remarks')
        }),
    )

admin.site.register(MaterialIssue, MaterialIssueAdmin)

admin.site.register(ItemsToIssue, ItemsToIssueAdmin)
