from core.models import (
    Inquiry, Quotation, PurchaseOrder, SalesOrder as CoreSalesOrder, Invoice, CustomerProfile,
    SalesOrderSeries as CoreSalesOrderSeries, InvoiceSeries as CoreInvoiceSeries,
)

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

class SalesOrderSeries(CoreSalesOrderSeries):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'Sales Order Series'
        verbose_name_plural = 'Sales Order Series'

class SalesInvoiceSeries(CoreInvoiceSeries):
    class Meta:
        proxy = True
        app_label = 'sales'
        verbose_name = 'Invoice Series'
        verbose_name_plural = 'Invoice Series'

