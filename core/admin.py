from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from .models import (Company, User, CustomerProfile, Division, ProductCategory, ProductSubCategory, Product, ProductDocument, Inquiry, InquiryItem, Quotation, QuotationItem, PurchaseOrder, SalesOrderSeries, SalesOrder, SalesOrderItem, InvoiceSeries, Invoice, InvoiceItem, Payment, AMCContract, ServiceTicket, Employee)

# NOA ERP Custom Branding Configurations
admin.site.site_header = "NOA ERP Administration"
admin.site.site_title = "NOA ERP Portal"
admin.site.index_title = "Welcome to NOA ERP Command Center"

# ── Custom app/model ordering ──────────────────────────────────
# Django's stock admin groups models by app (already yields "Sales & CRM",
# "Service Hub", "Product Master" via each app's AppConfig.verbose_name) but
# orders both apps and models alphabetically. Override with a fixed business
# priority order instead.
_APP_ORDER = ['sales', 'service', 'inventory', 'core', 'auth']
_MODEL_ORDER = [
    'SalesInquiry', 'SalesCustomerProfile', 'SalesQuotation', 'SalesPurchaseOrder',
    'SalesOrder', 'SalesInvoice',
    'ServiceServiceTicket', 'ServiceAMCContract',
    'InventoryDivision', 'InventoryProductCategory', 'InventoryProductSubCategory',
    'InventoryProduct', 'InventoryProductDocument',
    'Company', 'InvoiceSeries', 'SalesOrderSeries', 'Employee', 'User',
]


def _ordered_app_list(self, request, app_label=None):
    app_list = self._original_get_app_list(request, app_label=app_label)

    def app_key(app):
        try:
            return _APP_ORDER.index(app['app_label'])
        except ValueError:
            return len(_APP_ORDER)

    for app in app_list:
        app['models'].sort(key=lambda m: _MODEL_ORDER.index(m['object_name']) if m['object_name'] in _MODEL_ORDER else len(_MODEL_ORDER))
    app_list.sort(key=app_key)
    return app_list


admin.site._original_get_app_list = admin.site.get_app_list
admin.site.get_app_list = _ordered_app_list.__get__(admin.site)

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    list_display = ('name', 'brand_name', 'business_type', 'industry_type', 'is_active', 'created_at')
    search_fields = ('name', 'brand_name', 'gstin', 'pan')
    list_filter = ('is_active', 'business_type', 'industry_type', 'state')
    
    fieldsets = (
        ('Business Identity', {
            'fields': ('name', 'brand_name', 'logo', 'business_type', 'industry_type', 'website', 'is_active')
        }),
        ('Indian Statutory Details', {
            'fields': ('gstin', 'pan', 'cin', 'tan', 'msme_number', 'gst_state_code')
        }),
        ('Registered Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'pincode')
        }),
        ('Contact Details', {
            'fields': ('contact_email', 'contact_phone', 'alternate_phone')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'bank_account_number', 'bank_ifsc', 'bank_branch')
        }),
    )

@admin.register(User)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    list_display = ('username', 'email', 'company', 'role', 'is_staff')
    list_filter = ('role', 'company', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('NOA ERP Multi-Tenant Info', {'fields': ('company', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('NOA ERP Multi-Tenant Info', {'fields': ('company', 'role')}),
    )

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    list_display = ('employee_code', 'user', 'designation', 'department', 'status', 'company')
    list_filter = ('department', 'status', 'company')
    search_fields = ('employee_code', 'user__username', 'user__first_name', 'user__last_name', 'designation')
    fieldsets = (
        ('Account Info', {'fields': ('user', 'company', 'employee_code', 'status')}),
        ('Professional Details', {'fields': ('designation', 'department', 'date_of_joining', 'years_of_experience', 'specific_expertise', 'education_qualification')}),
        ('Contact Details', {'fields': ('contact_number', 'emergency_contact', 'address')}),
    )

class CustomerProfileAdmin(ImportExportModelAdmin):
    list_display = ('business_name', 'user', 'company', 'gst_number')
    list_filter = ('company',)
    search_fields = ('business_name', 'user__username')

class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    fields = ('title', 'document_type', 'division', 'category', 'subcategory', 'product', 'file')
    extra = 1
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('division', 'category', 'subcategory', 'product')

class DivisionAdmin(ImportExportModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)
    search_fields = ('name',)

class ProductCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'division', 'company')
    list_filter = ('company', 'division')
    search_fields = ('name',)
    inlines = [ProductDocumentInline]
    
    fieldsets = (
        ('Category Details', {
            'fields': ('company', 'division', 'name', 'description')
        }),
    )

class ProductSubCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'category', 'category__division', 'company')
    list_filter = ('company', 'category__division', 'category')
    search_fields = ('name', 'category__name')
    
    fieldsets = (
        ('Sub-Category Details', {
            'fields': ('company', 'category', 'name', 'description')
        }),
    )

class ProductAdmin(ImportExportModelAdmin):
    list_display = ('sku', 'name', 'model_number', 'division', 'category', 'subcategory', 'series', 'model_year', 'base_price', 'mrp', 'availability_status', 'is_active')
    list_filter = ('company', 'division', 'category', 'subcategory', 'availability_status', 'is_active')
    search_fields = ('sku', 'name', 'model_number', 'series')
    inlines = [ProductDocumentInline]
    
    fieldsets = (
        ('Product Identity', {
            'fields': ('company', 'division', 'category', 'subcategory', 'name', 'sku', 'model_number')
        }),
        ('Specifications', {
            'fields': ('specifications', 'series', 'model_year')
        }),
        ('Pricing', {
            'fields': ('base_price', 'mrp')
        }),
        ('Availability', {
            'fields': ('availability_status', 'is_active')
        }),
        ('Links & Documents', {
            'fields': ('product_url', 'brochure_url')
        }),
        ('Terms', {
            'fields': ('product_specific_terms',)
        }),
    )
    
from django.utils.html import format_html

class ProductDocumentAdmin(ImportExportModelAdmin):
    list_display = ('title', 'document_type', 'division', 'category', 'subcategory', 'product', 'download_link')
    list_filter = ('company', 'document_type', 'division', 'category', 'subcategory')
    search_fields = ('title', 'product__name', 'product__sku')
    
    fieldsets = (
        ('Document Details', {
            'fields': ('company', 'title', 'document_type', 'file')
        }),
        ('Product Hierarchy', {
            'fields': ('division', 'category', 'subcategory', 'product')
        }),
    )
    
    def download_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank" class="button">Download</a>', obj.file.url)
        return "-"
    download_link.short_description = "Download"
    download_link.allow_tags = True

class InquiryItemInline(admin.TabularInline):
    model = InquiryItem
    fields = ('division', 'category', 'subcategory', 'product', 'quantity')
    extra = 1

class InquiryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'company', 'source', 'phone', 'status', 'assigned_to', 'created_at')
    list_filter = ('company', 'source', 'status', 'assigned_to', 'created_at')
    search_fields = ('name', 'phone', 'email', 'requirement')
    inlines = [InquiryItemInline]
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('company', 'customer_profile', 'source', 'name', 'phone', 'email', 'requirement')
        }),
        ('Sales Tracking', {
            'fields': ('status', 'assigned_to')
        }),
    )

class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    fields = ('division', 'category', 'subcategory', 'product', 'quantity', 'unit_price')
    extra = 1

from django.utils.html import format_html
from django.urls import reverse

class QuotationAdmin(ImportExportModelAdmin):
    list_display = ('quotation_number', 'company', 'get_customer_name', 'status', 'prepared_by', 'created_at', 'download_pdf')
    list_filter = ('company', 'status', 'prepared_by')
    search_fields = ('quotation_number', 'inquiry__name', 'customer__business_name')
    readonly_fields = ('quotation_number', 'get_subtotal_display', 'get_final_total_display')
    inlines = [QuotationItemInline]
    
    fieldsets = (
        ('Target Audience', {
            'fields': ('quotation_number', 'company', 'inquiry', 'customer')
        }),
        ('Terms & Validity', {
            'fields': ('valid_until', 'terms_and_conditions')
        }),
        ('Discounts & Totals (Admin Only)', {
            'fields': ('admin_discount_percent', 'get_subtotal_display', 'get_final_total_display', 'status')
        }),
        ('Approvals', {
            'fields': ('prepared_by',)
        }),
    )

    def get_customer_name(self, obj):
        return obj.inquiry.name if obj.inquiry else (obj.customer.business_name if obj.customer else 'Unknown')
    get_customer_name.short_description = 'Customer / Inquiry'
    
    def get_subtotal_display(self, obj):
        return obj.get_subtotal()
    get_subtotal_display.short_description = 'Subtotal'

    def get_final_total_display(self, obj):
        return obj.get_final_total()
    get_final_total_display.short_description = 'Final Total (After Discount)'

    def download_pdf(self, obj):
        url = reverse('generate_pdf_quotation', args=[obj.id])
        return format_html('<a class="btn btn-sm btn-info" href="{}" target="_blank">PDF</a>', url)
    download_pdf.short_description = "Action"
    download_pdf.allow_tags = True
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if not change and obj.inquiry and obj.items.count() == 0:
            from core.models import QuotationItem
            for item in obj.inquiry.items.all():
                if item.product:
                    QuotationItem.objects.create(
                        quotation=obj,
                        division=item.division,
                        category=item.category,
                        subcategory=item.subcategory,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.base_price
                    )

class PurchaseOrderAdmin(ImportExportModelAdmin):
    list_display = ('po_number', 'company', 'customer', 'quotation', 'po_date', 'po_amount', 'status', 'get_sales_order_link')
    list_filter = ('company', 'status', 'po_date')
    search_fields = ('po_number', 'customer__business_name', 'quotation__quotation_number')
    fieldsets = (
        ('PO Details', {
            'fields': ('company', 'quotation', 'customer', 'po_number', 'po_date', 'po_file')
        }),
        ('Payment Terms', {
            'fields': ('payment_terms', 'po_amount')
        }),
        ('Status', {
            'fields': ('status',),
            'description': 'Setting status to "Confirmed" auto-generates an internal Sales Order.'
        }),
    )

    def get_sales_order_link(self, obj):
        so = getattr(obj, 'sales_order', None)
        if not so:
            return '-'
        return so.sales_order_number or 'Draft (no active series)'
    get_sales_order_link.short_description = 'Sales Order'

@admin.register(SalesOrderSeries)
class SalesOrderSeriesAdmin(ImportExportModelAdmin):
    list_display = ('name', 'prefix', 'next_number', 'is_active', 'company')
    list_filter = ('company', 'is_active')

class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    fields = ('division', 'category', 'subcategory', 'product', 'quantity', 'unit_price')
    extra = 0

class SalesOrderAdmin(ImportExportModelAdmin):
    list_display = ('sales_order_number', 'company', 'customer', 'purchase_order', 'order_date', 'expected_delivery_date', 'status')
    list_filter = ('company', 'status', 'order_date')
    search_fields = ('sales_order_number', 'customer__business_name', 'purchase_order__po_number')
    readonly_fields = ('sales_order_number', 'purchase_order', 'quotation')
    inlines = [SalesOrderItemInline]

    fieldsets = (
        ('Sales Order Details', {
            'fields': ('company', 'series', 'sales_order_number', 'purchase_order', 'quotation', 'customer')
        }),
        ('Fulfilment', {
            'fields': ('expected_delivery_date', 'status')
        }),
    )

@admin.register(InvoiceSeries)
class InvoiceSeriesAdmin(ImportExportModelAdmin):
    list_display = ('name', 'prefix', 'next_number', 'company')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    fields = ('division', 'category', 'subcategory', 'product', 'quantity', 'unit_price')
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

class InvoiceAdmin(ImportExportModelAdmin):
    list_display = ('invoice_number', 'company', 'customer', 'date', 'status', 'get_grand_total', 'get_balance_due', 'download_pdf')
    list_filter = ('company', 'status', 'series', 'date')
    search_fields = ('invoice_number', 'customer__business_name')
    readonly_fields = ('invoice_number', 'get_subtotal_display', 'get_tax_amount_display', 'get_grand_total_display', 'get_balance_due_display')
    inlines = [InvoiceItemInline, PaymentInline]
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('company', 'series', 'invoice_number', 'quotation', 'purchase_order', 'customer', 'due_date')
        }),
        ('Tax & Totals', {
            'fields': ('gst_percent', 'get_subtotal_display', 'get_tax_amount_display', 'get_grand_total_display', 'get_balance_due_display')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )

    def get_subtotal_display(self, obj):
        return obj.get_subtotal()
    get_subtotal_display.short_description = 'Subtotal'

    def get_tax_amount_display(self, obj):
        return obj.get_tax_amount()
    get_tax_amount_display.short_description = 'Tax Amount'

    def get_grand_total_display(self, obj):
        return obj.get_grand_total()
    get_grand_total_display.short_description = 'Grand Total'

    def get_balance_due_display(self, obj):
        return obj.get_balance_due()
    get_balance_due_display.short_description = 'Balance Due'

    def download_pdf(self, obj):
        if obj.id:
            try:
                url = reverse('generate_pdf_invoice', args=[obj.id])
                return format_html('<a class="button" href="{}" target="_blank">Download PDF</a>', url)
            except:
                return "-"
        return "-"
    download_pdf.short_description = "Action"
    download_pdf.allow_tags = True

class AMCContractAdmin(ImportExportModelAdmin):
    list_display = ('customer', 'division', 'category', 'subcategory', 'product', 'serial_number', 'start_date', 'end_date', 'status', 'contract_type')
    list_filter = ('company', 'division', 'status', 'contract_type')
    search_fields = ('customer__business_name', 'serial_number', 'third_party_brand')
    fieldsets = (
        ('Contract Information', {
            'fields': ('company', 'customer', 'contract_type', 'start_date', 'end_date', 'status')
        }),
        ('Product Hierarchy', {
            'fields': ('division', 'category', 'subcategory', 'product')
        }),
        ('Product Details', {
            'fields': ('serial_number', 'third_party_brand', 'third_party_model')
        }),
        ('AMC Settings', {
            'fields': ('pm_visits_per_year', 'auto_generate_tickets')
        }),
    )

class ServiceTicketAdmin(ImportExportModelAdmin):
    list_display = ('id', 'ticket_type', 'issue_title', 'company', 'customer', 'priority', 'status', 'assigned_engineer')
    list_filter = ('company', 'status', 'priority', 'ticket_type')
    search_fields = ('issue_title', 'customer__business_name')
    fieldsets = (
        ('Ticket Information', {
            'fields': ('company', 'customer', 'division', 'category', 'subcategory', 'product', 'issue_title', 'description')
        }),
        ('Status & Assignment', {
            'fields': ('priority', 'status', 'assigned_engineer')
        }),
        ('Resolution', {
            'fields': ('resolution_notes', 'resolved_at')
        }),
    )
