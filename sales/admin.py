from django.contrib import admin
from .models import SalesInquiry, SalesQuotation, SalesPurchaseOrder, SalesOrder, SalesInvoice, SalesCustomerProfile
from core.admin import InquiryAdmin, QuotationAdmin, PurchaseOrderAdmin, SalesOrderAdmin, InvoiceAdmin, CustomerProfileAdmin

admin.site.register(SalesInquiry, InquiryAdmin)
admin.site.register(SalesQuotation, QuotationAdmin)
admin.site.register(SalesPurchaseOrder, PurchaseOrderAdmin)
admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesInvoice, InvoiceAdmin)
admin.site.register(SalesCustomerProfile, CustomerProfileAdmin)
