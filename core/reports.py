"""
Universal Reports Center registry - one entry per report available across every
department. Each entry defines which model/date field to filter by and which
columns to show; the Reports Center view (core/views.py) handles date-range
filtering and PDF/Excel/CSV generation generically from this registry.
"""
from .models import (
    Inquiry, Quotation, SalesOrder, Invoice,
    Project, PurchaseRequisition,
    ServiceTicket, Equipment, AMCContract,
    StockTransaction, StockItem,
    SupplierPurchaseOrder,
    Employee,
    Supplier,
)

REPORTS = {
    'sales_inquiries': {
        'label': 'Sales Inquiries', 'department': 'Sales & CRM', 'model': Inquiry, 'date_field': 'created_at',
        'columns': [
            ('Prospect', lambda o: o.name),
            ('Phone', lambda o: o.phone),
            ('Source', lambda o: o.get_source_display()),
            ('Sale Type', lambda o: o.get_sale_type_display()),
            ('Status', lambda o: o.get_status_display()),
            ('Date', lambda o: o.created_at.date() if o.created_at else None),
        ],
    },
    'sales_quotations': {
        'label': 'Quotations', 'department': 'Sales & CRM', 'model': Quotation, 'date_field': 'created_at',
        'columns': [
            ('Quotation #', lambda o: o.quotation_number),
            ('Customer', lambda o: o.customer.business_name if o.customer else (o.inquiry.name if o.inquiry else '-')),
            ('Status', lambda o: o.get_status_display()),
            ('Total (₹)', lambda o: o.get_final_total()),
            ('Date', lambda o: o.created_at.date() if o.created_at else None),
        ],
    },
    'sales_orders': {
        'label': 'Sales Orders', 'department': 'Sales & CRM', 'model': SalesOrder, 'date_field': 'order_date',
        'columns': [
            ('SO #', lambda o: o.sales_order_number),
            ('Customer', lambda o: o.customer.business_name),
            ('Status', lambda o: o.get_status_display()),
            ('Order Date', lambda o: o.order_date),
            ('Expected Delivery', lambda o: o.expected_delivery_date),
        ],
    },
    'sales_invoices': {
        'label': 'Invoices', 'department': 'Sales & CRM', 'model': Invoice, 'date_field': 'date',
        'columns': [
            ('Invoice #', lambda o: o.invoice_number),
            ('Customer', lambda o: o.customer.business_name),
            ('Status', lambda o: o.get_status_display()),
            ('Grand Total (₹)', lambda o: o.get_grand_total()),
            ('Balance Due (₹)', lambda o: o.get_balance_due()),
            ('Date', lambda o: o.date),
        ],
    },
    'project_projects': {
        'label': 'Projects', 'department': 'Project Department', 'model': Project, 'date_field': 'start_date',
        'columns': [
            ('Project #', lambda o: o.project_number),
            ('Customer', lambda o: o.customer.business_name),
            ('Status', lambda o: o.get_status_display()),
            ('Start Date', lambda o: o.start_date),
            ('Expected Completion', lambda o: o.expected_completion_date),
        ],
    },
    'project_requisitions': {
        'label': 'Purchase Requisitions', 'department': 'Project Department', 'model': PurchaseRequisition, 'date_field': 'created_at',
        'columns': [
            ('PR #', lambda o: o.pr_number),
            ('Project', lambda o: o.project.project_number),
            ('Status', lambda o: o.get_status_display()),
            ('Date', lambda o: o.created_at.date() if o.created_at else None),
        ],
    },
    'service_tickets': {
        'label': 'Service Tickets', 'department': 'Service Department', 'model': ServiceTicket, 'date_field': 'created_at',
        'columns': [
            ('Ticket #', lambda o: o.ticket_number),
            ('Customer', lambda o: o.customer.business_name),
            ('Problem Type', lambda o: o.get_problem_type_display() if o.problem_type else '-'),
            ('Status', lambda o: o.get_status_display()),
            ('Outcome', lambda o: o.get_outcome_display() if o.outcome else '-'),
            ('Date', lambda o: o.created_at.date() if o.created_at else None),
        ],
    },
    'service_equipment': {
        'label': 'Equipment', 'department': 'Service Department', 'model': Equipment, 'date_field': 'created_at',
        'columns': [
            ('Asset #', lambda o: o.asset_number),
            ('Customer', lambda o: o.customer.business_name),
            ('Warranty Until', lambda o: o.warranty_end_date),
            ('AMC Until', lambda o: o.amc_end_date),
            ('Registered On', lambda o: o.created_at.date() if o.created_at else None),
        ],
    },
    'service_amc': {
        'label': 'AMC Contracts', 'department': 'Service Department', 'model': AMCContract, 'date_field': 'start_date',
        'columns': [
            ('Customer', lambda o: o.customer.business_name),
            ('Status', lambda o: o.get_status_display()),
            ('Start Date', lambda o: o.start_date),
            ('End Date', lambda o: o.end_date),
        ],
    },
    'store_transactions': {
        'label': 'Stock Transactions', 'department': 'Store Department', 'model': StockTransaction, 'date_field': 'transaction_date',
        'columns': [
            ('Voucher #', lambda o: o.voucher_number),
            ('Type', lambda o: o.get_transaction_type_display()),
            ('Item', lambda o: o.stock_item.name),
            ('Qty', lambda o: o.quantity),
            ('Godown', lambda o: o.godown.name),
            ('Date', lambda o: o.transaction_date),
        ],
    },
    'store_stock_items': {
        'label': 'Stock Items (Current Balance)', 'department': 'Store Department', 'model': StockItem, 'date_field': None,
        'columns': [
            ('Item Code', lambda o: o.item_code),
            ('Name', lambda o: o.name),
            ('Category', lambda o: o.category.name),
            ('Unit', lambda o: o.get_unit_display()),
            ('Balance', lambda o: o.get_stock_balance()),
            ('Reorder Level', lambda o: o.reorder_level),
        ],
    },
    'purchase_orders': {
        'label': 'Purchase Orders (Supplier)', 'department': 'Purchase Department', 'model': SupplierPurchaseOrder, 'date_field': 'order_date',
        'columns': [
            ('PO #', lambda o: o.po_number),
            ('Supplier', lambda o: o.supplier.name),
            ('Status', lambda o: o.get_status_display()),
            ('Grand Total (₹)', lambda o: o.get_grand_total()),
            ('Order Date', lambda o: o.order_date),
        ],
    },
    'hr_employees': {
        'label': 'Employees', 'department': 'HR & Admin', 'model': Employee, 'date_field': 'date_of_joining',
        'columns': [
            ('Employee Code', lambda o: o.employee_code),
            ('Name', lambda o: o.user.get_full_name() or o.user.username),
            ('Designation', lambda o: o.designation),
            ('Department', lambda o: o.department),
            ('Status', lambda o: o.get_status_display()),
            ('Date of Joining', lambda o: o.date_of_joining),
        ],
    },
    'master_suppliers': {
        'label': 'Suppliers', 'department': 'Master', 'model': Supplier, 'date_field': None,
        'columns': [
            ('Name', lambda o: o.name),
            ('Contact Person', lambda o: o.contact_person),
            ('Phone', lambda o: o.phone),
            ('Payment Terms', lambda o: o.payment_terms),
            ('Active', lambda o: 'Yes' if o.is_active else 'No'),
        ],
    },
}

# Departments in dashboard/menu order, used to group the report picker's <optgroup>s.
REPORT_DEPARTMENT_ORDER = [
    'Sales & CRM', 'Project Department', 'Service Department', 'Store Department',
    'Purchase Department', 'HR & Admin', 'Master',
]
