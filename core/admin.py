import os
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.staticfiles import finders
from django.http import HttpResponseRedirect
from import_export.admin import ImportExportModelAdmin
from .models import (Company, User, CustomerProfile, Division, ProductCategory, ProductSubCategory, Product, ProductDocument, Inquiry, InquiryItem, Quotation, QuotationItem, PurchaseOrder, SalesOrder, SalesOrderItem, Invoice, InvoiceItem, Payment, AMCContract, ServiceTicket, ServiceTicketPartUsed, Employee, EmployeeFamilyMember, EmployeeDocument, OfferLetter, OfferLetterAllowance, OfferLetterFacility, Godown, StockCategory, StockSubCategory, StockItem, StockItemSerial, StockItemPiece, StockTransaction, RefillLog, Project, PurchaseRequisition, PurchaseRequisitionItem, Supplier, SupplierQuote, SupplierPurchaseOrder, SupplierPurchaseOrderItem, Equipment, EquipmentPartReplacement)

# NOA ERP Custom Branding Configurations
admin.site.site_header = "Network Office Automation ERP Software"
admin.site.site_title = "NOA ERP Portal"
admin.site.index_title = "Welcome to NOA ERP Command Center"


class SerialSelectMediaMixin:
    """Loads js/serial_select_admin.js with a cache-busting ?v= query string computed fresh
    on every request - a plain `class Media` tuple is only ever evaluated once, at process
    startup, so edits to the JS file wouldn't otherwise be picked up by browsers that already
    cached the old copy until the dev server itself restarts."""
    @property
    def media(self):
        base = super().media
        found = finders.find('js/serial_select_admin.js')
        version = int(os.path.getmtime(found)) if found else 0
        return base + forms.Media(js=(f'/static/js/serial_select_admin.js?v={version}',))


# ── Custom app/model ordering ──────────────────────────────────
# Django's stock admin groups models by app (already yields "Sales & CRM",
# "Service Department", "Product Master" via each app's AppConfig.verbose_name) but
# orders both apps and models alphabetically. Override with a fixed business
# priority order instead.
_APP_ORDER = ['sales', 'project', 'service', 'store', 'purchase', 'hr', 'core', 'auth']
_MODEL_ORDER = [
    'SalesInquiry', 'SalesCustomerProfile', 'SalesQuotation', 'SalesPurchaseOrder',
    'SalesOrder', 'SalesInvoice', 'SalesOrderSeries', 'SalesInvoiceSeries',
    'Project', 'PurchaseRequisition',
    'ServiceEquipment', 'ServiceServiceTicket', 'PendingComplaints', 'ServiceAMCContract',
    'StoreGodown', 'StoreStockItem', 'PurchaseInward', 'MaterialIssue', 'RefillEntry',
    'PendingReturnableItems', 'ItemsToIssue',
    'ItemsToPurchase', 'SupplierPurchaseOrder',
    'HREmployee', 'HROfferLetter',
    'Company', 'Supplier',
    'InventoryDivision', 'InventoryProductCategory', 'InventoryProductSubCategory',
    'InventoryProduct', 'InventoryProductDocument',
    'User',
]
# These stay fully registered/reachable (via links/buttons on their parent page) but
# don't need their own entry in the main menu.
# Stock Report also lives here - it's reached via the "Print Stock Report" button on
# the Stock Items page, not its own tab.
_HIDDEN_FROM_MENU = {
    'StoreStockCategory', 'StoreStockSubCategory', 'StoreStockTransaction', 'StoreStockItemSerial', 'StoreStockItemPiece',
    # Product hierarchy is managed from the Products page (object-tools buttons),
    # so only 'Products' itself appears under Master.
    'InventoryDivision', 'InventoryProductCategory', 'InventoryProductSubCategory', 'InventoryProductDocument',
    # One-time numbering setup, reached via the "Format Management" buttons on the
    # Sales Order / Invoice pages instead of their own tabs.
    'SalesOrderSeries', 'SalesInvoiceSeries',
    # Ticked directly on the AMC Contract / Equipment forms; reached via the
    # "Manage Coverage Items" button on those pages instead of its own tab.
    'ServiceAMCCoverageItem',
}


def _ordered_app_list(self, request, app_label=None):
    app_list = self._original_get_app_list(request, app_label=app_label)

    def app_key(app):
        try:
            return _APP_ORDER.index(app['app_label'])
        except ValueError:
            return len(_APP_ORDER)

    # Fold the Product Master (inventory) group's models into Master, so
    # product/catalog masters live under one setup section instead of their own tab.
    inventory_app = next((a for a in app_list if a['app_label'] == 'inventory'), None)
    core_app = next((a for a in app_list if a['app_label'] == 'core'), None)
    if inventory_app and core_app:
        core_app['models'].extend(inventory_app['models'])
        app_list.remove(inventory_app)

    for app in app_list:
        app['models'] = [m for m in app['models'] if m['object_name'] not in _HIDDEN_FROM_MENU]
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

class EmployeeFamilyMemberInline(admin.TabularInline):
    model = EmployeeFamilyMember
    fields = ('name', 'relation', 'date_of_birth', 'contact_number')
    extra = 1

class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    fields = ('document_type', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    extra = 1

class EmployeeAdmin(ImportExportModelAdmin):
    list_display = ('employee_code', 'user', 'designation', 'department', 'status', 'company')
    list_filter = ('department', 'status', 'company')
    search_fields = ('employee_code', 'user__username', 'user__first_name', 'user__last_name', 'designation')
    inlines = [EmployeeFamilyMemberInline, EmployeeDocumentInline]
    change_form_template = 'admin/hr/hremployee/change_form.html'
    fieldsets = (
        ('Account Info', {'fields': ('user', 'company', 'employee_code', 'status')}),
        ('Professional Details', {'fields': ('designation', 'department', 'date_of_joining', 'years_of_experience', 'specific_expertise', 'education_qualification')}),
        ('Personal Details', {'fields': ('date_of_birth', 'blood_group', 'marriage_anniversary')}),
        ('Contact Details', {'fields': ('contact_number', 'emergency_contact')}),
        ('Address', {'fields': ('present_address', 'permanent_address')}),
        ('Bank Details', {'fields': ('bank_account_holder_name', 'bank_account_number', 'bank_ifsc_code', 'bank_name', 'bank_branch')}),
        ('CRM Communication & Printing Preferences', {
            'fields': ('whatsapp_number', 'preferred_printer'),
            'description': "This user's own settings for sending/printing from the CRM. Their login Email (Master › Users) is used as the From/Reply-To address whenever they email a document from the system."
        }),
    )


class OfferLetterAllowanceInline(admin.TabularInline):
    model = OfferLetterAllowance
    extra = 1
    verbose_name = "Allowance"
    verbose_name_plural = "Allowances (add as many rows as needed - name and amount are both editable)"


class OfferLetterFacilityInline(admin.TabularInline):
    model = OfferLetterFacility
    extra = 1
    verbose_name = "Other Facility"
    verbose_name_plural = "Other Facilities Offered (add as many rows as needed - name and description are both editable)"


class OfferLetterAdmin(ImportExportModelAdmin):
    list_display = ('letter_number', 'candidate_name', 'designation', 'department', 'interview_date', 'expected_joining_date', 'letter_date', 'download_pdf', 'email_link', 'whatsapp_link', 'company')
    list_filter = ('company', 'department', 'letter_date', 'interview_date')
    search_fields = ('letter_number', 'candidate_name', 'designation', 'candidate_email', 'candidate_phone')
    readonly_fields = ('letter_number', 'letter_date')
    inlines = [OfferLetterAllowanceInline, OfferLetterFacilityInline]
    fieldsets = (
        ('Letter Details', {
            'fields': ('company', 'letter_number', 'letter_date'),
            'description': "Letter number and date are generated automatically (e.g. NOA/OFFER LETTER/001/26-27)."
        }),
        ('Candidate Details', {
            'fields': ('candidate_title', 'candidate_name', 'candidate_address', 'candidate_email', 'candidate_phone')
        }),
        ('Interview Details', {
            'fields': ('interview_date', 'interviewed_by', 'interview_remarks'),
            'description': "Captured for your records only - none of this prints on the offer letter."
        }),
        ('Position Offered', {
            'fields': ('designation', 'department', 'expected_joining_date')
        }),
        ('Compensation', {
            'fields': ('monthly_remuneration', 'conveyance_allowance'),
            'description': "The amount in words is generated automatically on the printed letter. Add HRA, Special Allowance, or any other named allowance below."
        }),
        ('PF Calculation', {
            'fields': ('pf_applicable', 'pf_employee_contribution', 'pf_employer_contribution'),
            'description': "Tick to apply. Leave the amounts blank to auto-calculate at 12% of monthly remuneration on save, or type your own figures."
        }),
        ('ESIC Calculation', {
            'fields': ('esic_applicable', 'esic_employee_contribution', 'esic_employer_contribution'),
            'description': "Tick to apply. Leave the amounts blank to auto-calculate (0.75% / 3.25% of monthly remuneration) on save, or type your own figures."
        }),
        ('Link to Employee', {
            'fields': ('employee',),
            'description': "Optional - link this offer to their Employee record once created (e.g. after they join)."
        }),
    )

    def download_pdf(self, obj):
        if obj.id:
            url = reverse('generate_pdf_offer_letter', args=[obj.id])
            return format_html('<a class="button" href="{}" target="_blank">Print PDF</a>', url)
        return "-"
    download_pdf.short_description = "Print"

    def email_link(self, obj):
        if obj.id:
            url = reverse('email_offer_letter', args=[obj.id])
            return format_html('<a class="button" href="{}">Email</a>', url)
        return "-"
    email_link.short_description = "Email"

    def whatsapp_link(self, obj):
        if obj.id:
            url = reverse('whatsapp_share_offer_letter', args=[obj.id])
            return format_html('<a class="button" href="{}" target="_blank">WhatsApp</a>', url)
        return "-"
    whatsapp_link.short_description = "WhatsApp"

@admin.register(Supplier)
class SupplierAdmin(ImportExportModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'whatsapp_number', 'payment_terms', 'is_active', 'company')
    list_filter = ('company', 'is_active')
    search_fields = ('name', 'contact_person', 'phone', 'email', 'gstin', 'deals_in_items__name', 'deals_in_items__item_code')
    filter_horizontal = ('deals_in_items',)
    fieldsets = (
        ('Supplier Details', {
            'fields': ('company', 'name', 'contact_person', 'is_active')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'whatsapp_number', 'alternate_contact_person', 'alternate_contact_number', 'address')
        }),
        ('Statutory', {
            'fields': ('gstin', 'pan_number', 'tan_number')
        }),
        ('Business Terms', {
            'fields': ('payment_terms', 'deals_in_items')
        }),
        ('Bank Details', {
            'fields': ('bank_account_holder_name', 'bank_account_number', 'bank_ifsc_code', 'bank_name', 'bank_branch')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

class AMCCoverageItemAdmin(ImportExportModelAdmin):
    list_display = ('name', 'is_active', 'company')
    list_filter = ('company', 'is_active')
    search_fields = ('name',)

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

class ProductCategoryInline(admin.TabularInline):
    """Manage a Division's Product Categories directly on the Division page."""
    model = ProductCategory
    fields = ('name', 'description')
    extra = 1
    show_change_link = True

class DivisionAdmin(ImportExportModelAdmin):
    list_display = ('name', 'get_category_count', 'company')
    list_filter = ('company',)
    search_fields = ('name',)
    inlines = [ProductCategoryInline]

    def get_category_count(self, obj):
        return obj.productcategory_set.count()
    get_category_count.short_description = 'Product Categories'

class ProductSubCategoryInline(admin.TabularInline):
    """Manage a Category's Sub-Categories directly on the Product Category page."""
    model = ProductSubCategory
    fields = ('name', 'description')
    extra = 1
    show_change_link = True

class ProductCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'division', 'get_subcategory_count', 'company')
    list_filter = ('company', 'division')
    search_fields = ('name',)
    inlines = [ProductSubCategoryInline, ProductDocumentInline]

    fieldsets = (
        ('Category Details', {
            'fields': ('company', 'division', 'name', 'description')
        }),
    )

    def get_subcategory_count(self, obj):
        return obj.subcategories.count()
    get_subcategory_count.short_description = 'Sub-Categories'

class ProductInline(admin.TabularInline):
    """See/manage a Sub-Category's Products directly on the Sub-Category page."""
    model = Product
    fk_name = 'subcategory'
    fields = ('sku', 'name', 'model_number', 'base_price', 'availability_status', 'is_active')
    extra = 0
    show_change_link = True

class ProductSubCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'category', 'category__division', 'get_product_count', 'company')
    list_filter = ('company', 'category__division', 'category')
    search_fields = ('name', 'category__name')
    inlines = [ProductInline]

    fieldsets = (
        ('Sub-Category Details', {
            'fields': ('company', 'category', 'name', 'description')
        }),
    )

    def get_product_count(self, obj):
        return obj.product_set.count()
    get_product_count.short_description = 'Products'

class ProductAdmin(ImportExportModelAdmin):
    list_display = ('sku', 'name', 'model_number', 'division', 'category', 'subcategory', 'series', 'model_year', 'base_price', 'mrp', 'availability_status', 'is_active')
    list_filter = ('company', 'division', 'category', 'subcategory', 'availability_status', 'is_active')
    search_fields = ('sku', 'name', 'model_number', 'series')
    inlines = [ProductDocumentInline]
    # Divisions/Categories/Sub-Categories/Documents are hidden from the main menu;
    # this template adds object-tools buttons here to reach them (see _HIDDEN_FROM_MENU).
    change_list_template = 'admin/inventory/inventoryproduct/change_list.html'

    def changelist_view(self, request, extra_context=None):
        from django.urls import reverse
        extra_context = extra_context or {}
        extra_context['manage_divisions_url'] = reverse('admin:inventory_inventorydivision_changelist')
        extra_context['manage_product_categories_url'] = reverse('admin:inventory_inventoryproductcategory_changelist')
        extra_context['manage_product_subcategories_url'] = reverse('admin:inventory_inventoryproductsubcategory_changelist')
        extra_context['manage_product_documents_url'] = reverse('admin:inventory_inventoryproductdocument_changelist')
        return super().changelist_view(request, extra_context=extra_context)
    
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

from django.utils.html import format_html, format_html_join

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
    list_display = ('name', 'company', 'sale_type', 'source', 'phone', 'status', 'assigned_to', 'created_at')
    list_filter = ('company', 'sale_type', 'source', 'status', 'assigned_to', 'created_at')
    search_fields = ('name', 'phone', 'email', 'requirement')
    inlines = [InquiryItemInline]
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('company', 'customer_profile', 'sale_type', 'source', 'name', 'phone', 'email', 'requirement')
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
    readonly_fields = ('sales_order_number', 'purchase_order', 'quotation', 'get_material_consumption_display')
    inlines = [SalesOrderItemInline]
    # Sales Order Series is a one-time numbering setup, not its own menu tab -
    # reach it from here instead (see templates/admin/sales/salesorder/change_list.html).
    change_list_template = 'admin/sales/salesorder/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['format_management_url'] = reverse('admin:sales_salesorderseries_changelist')
        return super().changelist_view(request, extra_context=extra_context)

    fieldsets = (
        ('Sales Order Details', {
            'fields': ('company', 'series', 'sales_order_number', 'purchase_order', 'quotation', 'customer')
        }),
        ('Fulfilment', {
            'fields': ('expected_delivery_date', 'status')
        }),
        ('Material Issued for this Project (Store)', {
            'fields': ('get_material_consumption_display',),
            'description': "Issued minus Returned = quantity actually consumed on site, billable to the customer."
        }),
    )

    def get_material_consumption_display(self, obj):
        rows = obj.get_material_consumption() if obj.pk else []
        if not rows:
            return "No stock has been issued against this project yet."
        rows_html = format_html_join(
            '',
            '<tr><td>{}</td><td style="text-align:center">{}</td><td style="text-align:center">{}</td><td style="text-align:center"><strong>{}</strong></td></tr>',
            ((row['stock_item'], row['issued'], row['returned'], row['consumed']) for row in rows)
        )
        return format_html(
            '<table style="width:100%"><tr><th style="text-align:left">Item</th><th>Issued</th><th>Returned</th><th>Consumed (Billable)</th></tr>{}</table>',
            rows_html
        )
    get_material_consumption_display.short_description = "Material Consumption"

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
    # Invoice Series is a one-time numbering setup, not its own menu tab -
    # reach it from here instead (see templates/admin/sales/salesinvoice/change_list.html).
    change_list_template = 'admin/sales/salesinvoice/change_list.html'

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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['format_management_url'] = reverse('admin:sales_salesinvoiceseries_changelist')
        return super().changelist_view(request, extra_context=extra_context)

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
    filter_horizontal = ('coverage_items',)
    change_list_template = 'admin/service/serviceamccontract/change_list.html'
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
        ('Coverage', {
            'fields': ('coverage_items',),
            'description': "Tick everything covered under this contract. Use the \"Manage Coverage Items\" button above to add a new coverage type (e.g. a new part or service category)."
        }),
    )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['manage_coverage_items_url'] = reverse('admin:service_serviceamccoverageitem_changelist')
        return super().changelist_view(request, extra_context=extra_context)


# ── Equipment (Asset Register) ──────────────────────────────

class EquipmentPartReplacementInline(admin.TabularInline):
    """Replacing a part keeps the same Asset record - this logs what was swapped, when, and under what coverage."""
    model = EquipmentPartReplacement
    fields = ('stock_item', 'quantity', 'replaced_under', 'service_ticket', 'notes')
    extra = 0

class EquipmentAdmin(ImportExportModelAdmin):
    list_display = ('asset_number', 'customer', 'serial_number', 'model_number', 'installation_site', 'get_warranty_status', 'get_amc_status', 'is_active', 'company')
    list_filter = ('company', 'amc_type', 'is_active', 'division')
    search_fields = ('asset_number', 'serial_number', 'model_number', 'customer__business_name', 'installation_site')
    readonly_fields = ('asset_number',)
    filter_horizontal = ('amc_coverage_items',)
    inlines = [EquipmentPartReplacementInline]
    actions = ['print_equipment_report']
    change_list_template = 'admin/service/serviceequipment/change_list.html'

    fieldsets = (
        ('Asset Identity', {
            'fields': ('company', 'asset_number', 'customer', 'installation_site', 'is_active')
        }),
        ('Product', {
            'fields': ('division', 'category', 'subcategory', 'product', 'third_party_brand', 'model_number', 'serial_number', 'model_description', 'installation_date')
        }),
        ('Warranty', {
            'fields': ('warranty_start_date', 'warranty_end_date')
        }),
        ('AMC', {
            'fields': ('amc_type', 'amc_start_date', 'amc_end_date', 'services_per_period', 'amc_coverage_items')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def get_warranty_status(self, obj):
        if not obj.warranty_end_date:
            return '-'
        from django.utils import timezone
        live = obj.warranty_end_date >= timezone.now().date()
        color = '#16a34a' if live else '#999'
        return format_html('<span style="color:{};">{}</span>', color, obj.warranty_end_date)
    get_warranty_status.short_description = 'Warranty Until'

    def get_amc_status(self, obj):
        if obj.amc_type == 'none' or not obj.amc_end_date:
            return '-'
        from django.utils import timezone
        live = obj.amc_end_date >= timezone.now().date()
        color = '#16a34a' if live else '#dc2626'
        return format_html('<span style="color:{}; font-weight:700;">{}</span>', color, obj.amc_end_date)
    get_amc_status.short_description = 'AMC Until'

    def print_equipment_report(self, request, queryset):
        ids = ','.join(str(pk) for pk in queryset.values_list('pk', flat=True))
        url = reverse('generate_pdf_equipment_report') + f'?ids={ids}'
        return HttpResponseRedirect(url)
    print_equipment_report.short_description = "Print Equipment Report (PDF) for selected"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['equipment_report_url'] = reverse('generate_pdf_equipment_report')
        extra_context['manage_coverage_items_url'] = reverse('admin:service_serviceamccoverageitem_changelist')
        return super().changelist_view(request, extra_context=extra_context)


# ── Service Ticket ───────────────────────────────────────────

class ServiceTicketPartUsedInline(admin.TabularInline):
    model = ServiceTicketPartUsed
    fields = ('stock_item', 'quantity', 'notes')
    extra = 0

class ServiceTicketAdmin(ImportExportModelAdmin):
    list_display = ('ticket_number', 'ticket_type', 'problem_type', 'issue_title', 'customer', 'priority', 'status', 'get_outcome_badge', 'get_engineers', 'company')
    list_filter = ('company', 'status', 'outcome', 'priority', 'ticket_type', 'received_via')
    search_fields = ('ticket_number', 'issue_title', 'customer__business_name', 'reported_by_name', 'reported_by_mobile')
    readonly_fields = ('ticket_number',)
    filter_horizontal = ('assigned_engineers',)
    inlines = [ServiceTicketPartUsedInline]

    fieldsets = (
        ('Ticket Information', {
            'fields': ('company', 'ticket_number', 'customer', 'equipment', 'division', 'category', 'subcategory', 'product')
        }),
        ('How It Was Reported', {
            'fields': ('received_via', 'reported_by_name', 'reported_by_mobile')
        }),
        ('Complaint Details', {
            'fields': ('ticket_type', 'problem_type', 'issue_title', 'description', 'priority')
        }),
        ('Assignment & Status', {
            'fields': ('assigned_engineers', 'status')
        }),
        ('Visit Outcome', {
            'fields': ('outcome', 'pending_reason'),
            'description': "If the visit didn't resolve the complaint, mark it 'Pending' and select why - a pending ticket cannot be closed."
        }),
        ('Call Closure', {
            'fields': ('call_start_time', 'call_close_time', 'service_call_report'),
            'description': "A Service Call Report must be uploaded and Call Close Time set before this ticket can be Resolved/Closed."
        }),
        ('Remarks', {
            'fields': ('resolution_notes', 'customer_remarks', 'resolved_at')
        }),
    )

    def get_outcome_badge(self, obj):
        if obj.outcome == 'pending':
            return format_html('<span style="color:#dc2626; font-weight:700;">{}</span>', obj.get_pending_reason_display() or 'Pending')
        if obj.outcome == 'completed':
            return format_html('<span style="color:#16a34a; font-weight:700;">{}</span>', 'Completed')
        return '-'
    get_outcome_badge.short_description = 'Outcome'

    def get_engineers(self, obj):
        return ', '.join(e.user.get_full_name() or e.user.username for e in obj.assigned_engineers.all())
    get_engineers.short_description = 'Technicians'


class PendingComplaintsAdmin(ImportExportModelAdmin):
    """Every complaint still marked Pending - stays listed here day after day until it's actioned and closed."""
    list_display = ('ticket_number', 'customer', 'equipment', 'get_pending_reason_badge', 'get_days_pending', 'priority', 'get_engineers', 'company')
    list_filter = ('company', 'pending_reason', 'priority')
    search_fields = ('ticket_number', 'issue_title', 'customer__business_name')
    filter_horizontal = ('assigned_engineers',)
    fieldsets = (
        ('Ticket Information', {
            'fields': ('company', 'ticket_number', 'customer', 'equipment', 'issue_title', 'description', 'priority')
        }),
        ('Assignment & Status', {
            'fields': ('assigned_engineers', 'status')
        }),
        ('Visit Outcome', {
            'fields': ('outcome', 'pending_reason'),
            'description': "Once this complaint is actually resolved, change the Outcome to 'Completed', then close it from Service Tickets (with the Service Call Report). It will then disappear from this list."
        }),
        ('Call Closure', {
            'fields': ('call_start_time', 'call_close_time', 'service_call_report')
        }),
        ('Remarks', {
            'fields': ('resolution_notes', 'customer_remarks')
        }),
    )
    readonly_fields = ('ticket_number',)

    def get_pending_reason_badge(self, obj):
        return format_html('<span style="color:#dc2626; font-weight:700;">{}</span>', obj.get_pending_reason_display() or '-')
    get_pending_reason_badge.short_description = 'Pending Reason'

    def get_days_pending(self, obj):
        from django.utils import timezone
        days = (timezone.now() - obj.created_at).days
        return f"{days} day(s)"
    get_days_pending.short_description = 'Pending Since'

    def get_engineers(self, obj):
        return ', '.join(e.user.get_full_name() or e.user.username for e in obj.assigned_engineers.all())
    get_engineers.short_description = 'Technicians'


# ─────────────────────────────────────────────────────────────
# Store / Inventory Management
# ─────────────────────────────────────────────────────────────

class GodownAdmin(ImportExportModelAdmin):
    list_display = ('name', 'godown_type', 'parent_godown', 'location', 'company', 'is_active')
    list_filter = ('company', 'godown_type', 'is_active')
    search_fields = ('name', 'location')
    fieldsets = (
        ('Godown Details', {
            'fields': ('company', 'name', 'godown_type', 'parent_godown', 'location', 'is_active')
        }),
    )

class StockSubCategoryInline(admin.TabularInline):
    model = StockSubCategory
    fields = ('name', 'is_active')
    extra = 1

class StockCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'company', 'is_active')
    list_filter = ('company', 'is_active')
    search_fields = ('name',)
    inlines = [StockSubCategoryInline]
    fieldsets = (
        ('Category Details', {
            'fields': ('company', 'name', 'is_active')
        }),
    )

class StockSubCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'category', 'company', 'is_active')
    list_filter = ('company', 'category', 'is_active')
    search_fields = ('name', 'category__name')
    fieldsets = (
        ('Sub-Category Details', {
            'fields': ('company', 'category', 'name', 'is_active')
        }),
    )

class StockItemAdmin(ImportExportModelAdmin):
    list_display = ('item_code', 'name', 'category', 'subcategory', 'unit', 'reorder_level', 'get_total_stock', 'is_active', 'company')
    list_filter = ('company', 'category', 'subcategory', 'unit', 'is_active')
    search_fields = ('item_code', 'name')
    actions = ['print_stock_report']
    # ImportExportModelAdmin normally hardcodes change_list_template; setting it here
    # makes import_export use OUR template as its base instead (see init_change_list_template).
    change_list_template = 'admin/store/storestockitem/change_list.html'
    fieldsets = (
        ('Item Details', {
            'fields': ('company', 'item_code', 'name', 'category', 'subcategory', 'unit', 'linked_product')
        }),
        ('Stock Settings', {
            'fields': ('reorder_level', 'is_active', 'is_serialized', 'is_returnable', 'is_refillable', 'is_piece_tracked', 'notes')
        }),
    )

    def get_total_stock(self, obj):
        total = obj.get_stock_balance()
        if not obj.is_piece_tracked:
            return total
        pieces = obj.pieces.filter(status='in_stock').order_by('-quantity')
        if not pieces:
            return total
        pieces_html = format_html_join(
            ', ', '{}: {}',
            ((p.label, p.quantity) for p in pieces)
        )
        return format_html('{} {} <span style="color:#666; font-size:11px;">({} pieces - {})</span>', total, obj.get_unit_display(), pieces.count(), pieces_html)
    get_total_stock.short_description = 'Total Stock (All Godowns)'

    def print_stock_report(self, request, queryset):
        ids = ','.join(str(pk) for pk in queryset.values_list('pk', flat=True))
        url = reverse('generate_pdf_stock_report') + f'?ids={ids}'
        return HttpResponseRedirect(url)
    print_stock_report.short_description = "Print Stock Report (PDF) for selected items"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['stock_report_url'] = reverse('stock_report_filters')
        extra_context['manage_categories_url'] = reverse('admin:store_storestockcategory_changelist')
        extra_context['view_transactions_url'] = reverse('admin:store_storestocktransaction_changelist')
        extra_context['manage_serials_url'] = reverse('admin:store_storestockitemserial_changelist')
        extra_context['manage_pieces_url'] = reverse('admin:store_storestockitempiece_changelist')
        return super().changelist_view(request, extra_context=extra_context)


class StockItemSerialAdmin(ImportExportModelAdmin):
    list_display = ('serial_number', 'stock_item', 'status', 'godown')
    list_filter = ('status', 'stock_item__category', 'godown')
    search_fields = ('serial_number', 'stock_item__name', 'stock_item__item_code')
    fields = ('stock_item', 'serial_number', 'godown', 'status')


class StockItemPieceAdmin(ImportExportModelAdmin):
    list_display = ('label', 'stock_item', 'quantity', 'status', 'godown')
    list_filter = ('status', 'stock_item__category', 'godown')
    search_fields = ('label', 'stock_item__name', 'stock_item__item_code')
    fields = ('stock_item', 'label', 'quantity', 'godown', 'status')


class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For serialized/piece-tracked items, Quantity is derived from the picked
        # serials/pieces after save - default it to 0 so it never blocks submission.
        if not self.instance.pk:
            self.fields['quantity'].initial = 0


class StockTransactionAdmin(SerialSelectMediaMixin, ImportExportModelAdmin):
    form = StockTransactionForm
    list_display = ('voucher_number', 'transaction_type', 'stock_item', 'godown', 'quantity', 'destination_godown', 'sales_order', 'party_type', 'transaction_date', 'company')
    list_filter = ('company', 'transaction_type', 'godown', 'sales_order', 'party_type', 'transaction_date')
    search_fields = ('voucher_number', 'stock_item__name', 'stock_item__item_code', 'party_name', 'sales_order__sales_order_number')
    readonly_fields = ('voucher_number',)
    fieldsets = (
        ('Transaction', {
            'fields': ('company', 'voucher_number', 'transaction_type', 'stock_item', 'godown', 'quantity')
        }),
        ('Alternate Unit (Reference Only)', {
            'fields': ('transaction_uom', 'transaction_uom_quantity'),
            'description': "Optional: also record this transaction in a different unit for reference (e.g. what was purchased in). Doesn't affect Quantity above, which is always entered directly."
        }),
        ('Serial Numbers', {
            'fields': ('serials',),
            'description': "For serialized items only (e.g. AC IDU/ODU, tools, gas cylinders) - pick the specific unit(s) this transaction covers. Quantity is set automatically from your selection."
        }),
        ('Pieces', {
            'fields': ('pieces',),
            'description': "For piece-tracked items only (e.g. Copper Pipe cut lengths) - pick the specific piece(s) this transaction covers. Quantity is set automatically from the total of your selection."
        }),
        ('Project', {
            'fields': ('sales_order',),
            'description': "Link this transaction to the customer project it belongs to, so material issued/returned/consumed can be tracked and billed per project."
        }),
        ('Transfer (Main -> Sub Godown)', {
            'fields': ('destination_godown',),
            'description': "Required only for 'Transfer Out' transactions."
        }),
        ('Issue / Return - Party Details', {
            'fields': ('party_type', 'issued_to_employee', 'issued_to_customer', 'party_name', 'related_transaction'),
            'description': "Fill for 'Issued to Party' and 'Returned to Store' transactions."
        }),
        ('Notes', {
            'fields': ('handled_by', 'remarks')
        }),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get('object_id') if request.resolver_match else None
        if db_field.name == 'serials':
            qs = StockItemSerial.objects.filter(status__in=['in_stock', 'issued'])
            if object_id:
                qs = qs | StockItemSerial.objects.filter(transactions__pk=object_id)
            kwargs['queryset'] = qs.distinct().select_related('stock_item')
            kwargs['widget'] = forms.SelectMultiple(attrs={'data-statuses': 'in_stock,issued', 'size': 8})
        if db_field.name == 'pieces':
            qs = StockItemPiece.objects.filter(status__in=['in_stock', 'issued'])
            if object_id:
                qs = qs | StockItemPiece.objects.filter(transactions__pk=object_id)
            kwargs['queryset'] = qs.distinct().select_related('stock_item')
            kwargs['widget'] = forms.SelectMultiple(attrs={'data-piece-statuses': 'in_stock,issued', 'size': 8})
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.sync_serial_statuses()
        form.instance.sync_piece_statuses()


class RefillLogAdmin(ImportExportModelAdmin):
    list_display = ('serial_display', 'stock_item', 'old_serial_number', 'new_serial_number', 'godown', 'refill_date', 'handled_by', 'company')
    list_filter = ('company', 'stock_item', 'godown', 'refill_date')
    search_fields = ('old_serial_number', 'new_serial_number', 'serial__serial_number', 'stock_item__name')
    readonly_fields = ('old_serial_number',)
    fieldsets = (
        ('Refill Details', {
            'fields': ('company', 'stock_item', 'serial', 'new_serial_number', 'godown'),
            'description': "Log a refill for a reusable container (e.g. gas cylinder). Leave 'New Serial Number' blank if the bottle keeps the same number."
        }),
        ('Notes', {
            'fields': ('handled_by', 'remarks')
        }),
    )

    def serial_display(self, obj):
        return obj.serial.serial_number if obj.serial_id else '-'
    serial_display.short_description = 'Serial (current)'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'stock_item':
            kwargs['queryset'] = StockItem.objects.filter(is_refillable=True)
        if db_field.name == 'serial':
            kwargs['queryset'] = StockItemSerial.objects.filter(stock_item__is_refillable=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PendingReturnableItemsAdmin(ImportExportModelAdmin):
    """Report-only: Issue transactions of returnable items (e.g. Tools) still awaiting return.
    A row drops off automatically once returned (or scrapped, for a faulty tool)."""
    list_display = ('voucher_number', 'stock_item', 'get_pending_serials_display', 'get_pending_qty_display', 'party_type', 'issued_to_employee', 'issued_to_customer', 'party_name', 'transaction_date', 'get_days_pending_display', 'company')
    list_filter = ('company', 'godown', 'party_type', 'transaction_date')
    search_fields = ('voucher_number', 'stock_item__name', 'stock_item__item_code', 'party_name')

    def has_add_permission(self, request):
        return False

    def get_pending_serials_display(self, obj):
        if obj.stock_item.is_serialized:
            numbers = obj.get_pending_serials().values_list('serial_number', flat=True)
            return ", ".join(numbers) or '-'
        return '-'
    get_pending_serials_display.short_description = 'Pending Serial(s)'

    def get_pending_qty_display(self, obj):
        return obj.pending_return_quantity
    get_pending_qty_display.short_description = 'Qty Pending'

    def get_days_pending_display(self, obj):
        return obj.days_pending_return
    get_days_pending_display.short_description = 'Days Pending'

# ─────────────────────────────────────────────────────────────
# Project Department
# ─────────────────────────────────────────────────────────────

class PurchaseRequisitionItemInline(admin.TabularInline):
    model = PurchaseRequisitionItem
    fields = ('stock_item', 'quantity', 'get_current_stock_display', 'get_shortfall_display', 'get_recommended_purchase_display', 'notes')
    readonly_fields = ('get_current_stock_display', 'get_shortfall_display', 'get_recommended_purchase_display')
    extra = 1

    class Media:
        js = ('js/purchase_requisition_admin.js',)

    def get_current_stock_display(self, obj):
        if not obj or not obj.pk:
            return '-'
        return f"{obj.get_current_stock()} {obj.stock_item.get_unit_display()}"
    get_current_stock_display.short_description = 'Current Stock'

    def get_shortfall_display(self, obj):
        if not obj or not obj.pk:
            return '-'
        if obj.is_shortfall:
            return format_html('<span style="color:#dc2626; font-weight:700;">SHORT by {}</span>', obj.shortfall_qty)
        return format_html('<span style="color:#16a34a; font-weight:700;">{}</span>', 'In Stock')
    get_shortfall_display.short_description = 'Status'

    def get_recommended_purchase_display(self, obj):
        if not obj or not obj.pk or not obj.is_shortfall:
            return '-'
        unit = obj.stock_item.get_unit_display()
        return format_html(
            '<span style="color:#b45309; font-weight:700;">{} {}</span><br><span style="font-size:11px; color:#666;">(shortfall {} + MSL {})</span>',
            obj.recommended_purchase_qty, unit, obj.shortfall_qty, obj.stock_item.reorder_level,
        )
    get_recommended_purchase_display.short_description = 'To Purchase (incl. MSL)'


class ProjectAdmin(ImportExportModelAdmin):
    list_display = ('project_number', 'customer', 'sales_order', 'status', 'start_date', 'expected_completion_date', 'get_pr_count', 'company')
    list_filter = ('company', 'status')
    search_fields = ('project_number', 'customer__business_name', 'sales_order__sales_order_number')
    readonly_fields = ('project_number', 'sales_order')
    fieldsets = (
        ('Project Details', {
            'fields': ('company', 'project_number', 'sales_order', 'customer', 'name')
        }),
        ('Status & Timeline', {
            'fields': ('status', 'expected_completion_date', 'notes')
        }),
    )

    def get_pr_count(self, obj):
        url = reverse('admin:project_purchaserequisition_changelist') + f'?project__id__exact={obj.pk}'
        count = obj.purchase_requisitions.count()
        return format_html('<a href="{}">{} Requisition(s)</a>', url, count)
    get_pr_count.short_description = 'Purchase Requisitions'


class PurchaseRequisitionAdmin(ImportExportModelAdmin):
    list_display = ('pr_number', 'project', 'status', 'created_at', 'requested_by', 'get_shortfall_badge', 'download_pdf', 'email_link', 'company')
    list_filter = ('company', 'status', 'created_at')
    search_fields = ('pr_number', 'project__project_number', 'project__customer__business_name')
    readonly_fields = ('pr_number',)
    inlines = [PurchaseRequisitionItemInline]
    fieldsets = (
        ('Requisition Details', {
            'fields': ('company', 'pr_number', 'project', 'requested_by', 'status')
        }),
        ('Notes', {
            'fields': ('remarks',)
        }),
    )

    def get_shortfall_badge(self, obj):
        if obj.has_shortfall():
            return format_html('<span style="color:#dc2626; font-weight:700;">{}</span>', 'NEEDS PURCHASE')
        return format_html('<span style="color:#16a34a; font-weight:700;">{}</span>', 'FULLY IN STOCK')
    get_shortfall_badge.short_description = 'Stock Status'

    def download_pdf(self, obj):
        if obj.id:
            url = reverse('generate_pdf_purchase_requisition', args=[obj.id])
            return format_html('<a class="button" href="{}" target="_blank">Print PDF</a>', url)
        return "-"
    download_pdf.short_description = "Print"

    def email_link(self, obj):
        if obj.id:
            url = reverse('email_purchase_requisition', args=[obj.id])
            return format_html('<a class="button" href="{}">Email</a>', url)
        return "-"
    email_link.short_description = "Email"


# ─────────────────────────────────────────────────────────────
# Purchase Requisition items, split across Store and Purchase Departments.
# "is_shortfall" is a live property (always reflects *current* stock), so
# these views filter in Python rather than the DB, then re-wrap the
# matching PKs into a real queryset so admin pagination/sorting still work.
# ─────────────────────────────────────────────────────────────

class ItemsToIssueAdmin(ImportExportModelAdmin):
    """Store Department: PR lines already covered by current stock - ready to issue."""
    list_display = ('stock_item', 'purchase_requisition', 'get_project_link', 'quantity', 'get_current_stock_display', 'status')
    list_filter = ('status',)
    search_fields = ('stock_item__name', 'stock_item__item_code', 'purchase_requisition__pr_number', 'purchase_requisition__project__project_number')
    actions = ['mark_issued']
    fields = ('purchase_requisition', 'stock_item', 'quantity', 'status', 'notes')
    readonly_fields = ('purchase_requisition', 'stock_item', 'quantity')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        matching_pks = [obj.pk for obj in qs if obj.status == 'issued' or (obj.status == 'pending' and not obj.is_shortfall)]
        return qs.model.objects.filter(pk__in=matching_pks)

    def get_current_stock_display(self, obj):
        return f"{obj.get_current_stock()} {obj.stock_item.get_unit_display()}"
    get_current_stock_display.short_description = 'Current Stock'

    def get_project_link(self, obj):
        return obj.purchase_requisition.project.project_number
    get_project_link.short_description = 'Project'

    def mark_issued(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='issued')
        self.message_user(request, f"{updated} item(s) marked as Issued from Stock. Record the actual movement via Material Issue.")
    mark_issued.short_description = "Mark selected as Issued from Stock"


class SupplierQuoteInline(admin.TabularInline):
    """Price comparison: log quotes from multiple suppliers for this item, then mark the winner."""
    model = SupplierQuote
    fk_name = 'purchase_requisition_item'
    fields = ('supplier', 'quoted_price', 'delivery_days', 'is_selected', 'notes')
    extra = 1

class ItemsToPurchaseAdmin(ImportExportModelAdmin):
    """Purchase Department: PR lines short on stock - need external procurement."""
    list_display = ('stock_item', 'purchase_requisition', 'get_project_link', 'quantity', 'get_current_stock_display', 'get_recommended_purchase_display', 'get_best_quote_display', 'status')
    list_filter = ('status',)
    search_fields = ('stock_item__name', 'stock_item__item_code', 'purchase_requisition__pr_number', 'purchase_requisition__project__project_number')
    actions = ['mark_ordered', 'mark_received']
    fields = ('purchase_requisition', 'stock_item', 'quantity', 'status', 'notes')
    readonly_fields = ('purchase_requisition', 'stock_item', 'quantity')
    inlines = [SupplierQuoteInline]

    def get_best_quote_display(self, obj):
        selected = obj.supplier_quotes.filter(is_selected=True).first()
        if selected:
            return format_html('<b>{}</b> @ {}/unit', selected.supplier.name, selected.quoted_price)
        cheapest = obj.supplier_quotes.order_by('quoted_price').first()
        if cheapest:
            return format_html('{} quote(s), cheapest: {} @ {}/unit', obj.supplier_quotes.count(), cheapest.supplier.name, cheapest.quoted_price)
        return '-'
    get_best_quote_display.short_description = 'Price Comparison'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        matching_pks = [obj.pk for obj in qs if obj.status in ('ordered', 'received') or (obj.status == 'pending' and obj.is_shortfall)]
        return qs.model.objects.filter(pk__in=matching_pks)

    def get_current_stock_display(self, obj):
        return f"{obj.get_current_stock()} {obj.stock_item.get_unit_display()}"
    get_current_stock_display.short_description = 'Current Stock'

    def get_recommended_purchase_display(self, obj):
        return f"{obj.recommended_purchase_qty} {obj.stock_item.get_unit_display()}"
    get_recommended_purchase_display.short_description = 'To Purchase (incl. MSL)'

    def get_project_link(self, obj):
        return obj.purchase_requisition.project.project_number
    get_project_link.short_description = 'Project'

    def mark_ordered(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='ordered')
        self.message_user(request, f"{updated} item(s) marked as Purchase Ordered.")
    mark_ordered.short_description = "Mark selected as Purchase Ordered"

    def mark_received(self, request, queryset):
        updated = queryset.filter(status='ordered').update(status='received')
        self.message_user(request, f"{updated} item(s) marked as Received. Record the stock receipt via Purchase Inward.")
    mark_received.short_description = "Mark selected as Received"


# ─────────────────────────────────────────────────────────────
# Purchase Order (to Supplier)
# ─────────────────────────────────────────────────────────────

class SupplierPurchaseOrderItemInline(admin.TabularInline):
    model = SupplierPurchaseOrderItem
    fields = ('requisition_item', 'stock_item', 'quantity', 'unit_price', 'get_line_total_display')
    readonly_fields = ('get_line_total_display',)
    extra = 1

    def get_line_total_display(self, obj):
        if not obj or not obj.pk:
            return '-'
        return obj.get_line_total()
    get_line_total_display.short_description = 'Line Total'


class SupplierPurchaseOrderAdmin(ImportExportModelAdmin):
    list_display = ('po_number', 'supplier', 'project', 'status', 'order_date', 'get_grand_total_display', 'download_pdf', 'email_link', 'whatsapp_link', 'company')
    list_filter = ('company', 'status', 'supplier', 'order_date')
    search_fields = ('po_number', 'supplier__name', 'project__project_number')
    readonly_fields = ('po_number',)
    inlines = [SupplierPurchaseOrderItemInline]
    fieldsets = (
        ('Purchase Order Details', {
            'fields': ('company', 'po_number', 'supplier', 'project', 'status')
        }),
        ('Delivery', {
            'fields': ('expected_delivery_date', 'remarks')
        }),
    )

    def get_grand_total_display(self, obj):
        return obj.get_grand_total()
    get_grand_total_display.short_description = 'Grand Total'

    def download_pdf(self, obj):
        if obj.id:
            url = reverse('generate_pdf_supplier_po', args=[obj.id])
            return format_html('<a class="button" href="{}" target="_blank">Print PDF</a>', url)
        return "-"
    download_pdf.short_description = "Print"

    def email_link(self, obj):
        if obj.id:
            url = reverse('email_supplier_po', args=[obj.id])
            return format_html('<a class="button" href="{}">Email</a>', url)
        return "-"
    email_link.short_description = "Email"

    def whatsapp_link(self, obj):
        if obj.id:
            url = reverse('whatsapp_share_supplier_po', args=[obj.id])
            return format_html('<a class="button" href="{}" target="_blank">WhatsApp</a>', url)
        return "-"
    whatsapp_link.short_description = "WhatsApp"
