from core.models import Inquiry, Quotation, PurchaseOrder, SalesOrder as CoreSalesOrder, Invoice, CustomerProfile

class SalesInquiry(Inquiry):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'

class SalesQuotation(Quotation):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'

class SalesPurchaseOrder(PurchaseOrder):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'

class SalesOrder(CoreSalesOrder):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'Sales Order'
        verbose_name_plural = 'Sales Orders'

class SalesInvoice(Invoice):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

class SalesCustomerProfile(CustomerProfile):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'CustomerProfile'
        verbose_name_plural = 'Customer Profiles'

