from django import template
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from sales.models import SalesInquiry
from core.models import (
    CustomerProfile, ServiceTicket, AMCContract, Invoice, Quotation,
    SalesOrder, Project, PurchaseRequisitionItem, StockItem, SupplierPurchaseOrder,
)

register = template.Library()


def _bar(label, value, color):
    return {'label': label, 'value': value, 'color': color}


def _with_pcts(bars):
    """Scale each bar's width relative to the largest value in the group."""
    peak = max((b['value'] for b in bars), default=0)
    for b in bars:
        b['pct'] = round((b['value'] / peak) * 100) if peak else 0
    return bars


def _meter(label, dept_key, numerator, denominator, detail):
    """A single ratio-against-a-limit performance meter for one department."""
    if not denominator:
        return {'label': label, 'dept_key': dept_key, 'pct': None, 'detail': 'No data yet'}
    pct = round((numerator / denominator) * 100)
    if pct >= 70:
        severity = 'good'
    elif pct >= 40:
        severity = 'warning'
    else:
        severity = 'critical'
    return {'label': label, 'dept_key': dept_key, 'pct': pct, 'severity': severity, 'detail': detail}


@register.inclusion_tag('admin/kpi_dashboard.html', takes_context=True)
def render_dashboard_kpis(context):
    now = timezone.now()
    thirty_days_from_now = now + timedelta(days=30)

    active_items = list(StockItem.objects.filter(is_active=True))
    low_stock_items = [item for item in active_items if item.get_stock_balance() <= item.reorder_level]
    low_stock_count = len(low_stock_items)

    total_quotations = Quotation.objects.count()
    accepted_quotations = Quotation.objects.filter(status='accepted').count()

    total_tickets = ServiceTicket.objects.count()
    resolved_tickets = ServiceTicket.objects.filter(status__in=['resolved', 'closed']).count()

    total_projects = Project.objects.count()
    completed_projects = Project.objects.filter(status='completed').count()

    total_po = SupplierPurchaseOrder.objects.exclude(status='cancelled').count()
    received_po = SupplierPurchaseOrder.objects.filter(status='received').count()

    healthy_stock_count = len(active_items) - low_stock_count

    performance_meters = [
        _meter('Sales & CRM', 'sales', accepted_quotations, total_quotations,
               f'{accepted_quotations} of {total_quotations} quotations accepted'),
        _meter('Service Department', 'service', resolved_tickets, total_tickets,
               f'{resolved_tickets} of {total_tickets} tickets resolved'),
        _meter('Project Department', 'project', completed_projects, total_projects,
               f'{completed_projects} of {total_projects} projects completed'),
        _meter('Purchase Department', 'purchase', received_po, total_po,
               f'{received_po} of {total_po} purchase orders received'),
        _meter('Store Department', 'store', healthy_stock_count, len(active_items),
               f'{healthy_stock_count} of {len(active_items)} items at healthy stock'),
    ]

    open_inquiries_count = SalesInquiry.objects.exclude(status__in=['won', 'lost']).count()
    pending_quotations_count = Quotation.objects.filter(status__in=['draft', 'sent']).count()
    open_tickets_count = ServiceTicket.objects.filter(status__in=['open', 'assigned', 'in_progress']).count()
    active_projects_count = Project.objects.exclude(status__in=['completed', 'cancelled']).count()
    items_to_purchase_count = PurchaseRequisitionItem.objects.filter(status__in=['pending', 'ordered']).count()

    # Data for the "Graphical Comparison" dropdown chart - each option is a
    # small, cheap-to-compute set of bars sharing the same department/status
    # colour language used elsewhere on the dashboard (perf-dept-* colours).
    comparison_charts = {
        'workload': {
            'title': 'Open Workload by Department',
            'bars': _with_pcts([
                _bar('Sales & CRM', open_inquiries_count + pending_quotations_count, '#3b82f6'),
                _bar('Service Department', open_tickets_count, '#ec4899'),
                _bar('Project Department', active_projects_count, '#a855f7'),
                _bar('Purchase Department', items_to_purchase_count, '#f97316'),
                _bar('Store Department', low_stock_count, '#14b8a6'),
            ]),
        },
        'invoices': {
            'title': 'Invoices by Status',
            'bars': _with_pcts([
                _bar('Draft', Invoice.objects.filter(status='draft').count(), '#94a3b8'),
                _bar('Unpaid', Invoice.objects.filter(status='unpaid').count(), '#ef4444'),
                _bar('Partially Paid', Invoice.objects.filter(status='partial').count(), '#f59e0b'),
                _bar('Fully Paid', Invoice.objects.filter(status='paid').count(), '#10b981'),
            ]),
        },
        'quotations': {
            'title': 'Quotations by Status',
            'bars': _with_pcts([
                _bar('Draft', Quotation.objects.filter(status='draft').count(), '#94a3b8'),
                _bar('Sent to Customer', Quotation.objects.filter(status='sent').count(), '#0891b2'),
                _bar('Accepted', Quotation.objects.filter(status='accepted').count(), '#10b981'),
                _bar('Rejected', Quotation.objects.filter(status='rejected').count(), '#ef4444'),
            ]),
        },
    }

    return {
        'performance_meters': performance_meters,
        'comparison_charts': comparison_charts,
        # Sales
        'open_inquiries_count': open_inquiries_count,
        'pending_quotations_count': pending_quotations_count,
        'active_sales_orders_count': SalesOrder.objects.exclude(status__in=['completed', 'cancelled']).count(),
        'active_customers_count': CustomerProfile.objects.count(),
        'overdue_invoices_count': Invoice.objects.filter(status='unpaid', due_date__lt=now.date()).count(),
        # Service
        'open_tickets_count': open_tickets_count,
        'pending_complaints_count': ServiceTicket.objects.filter(outcome='pending').count(),
        'urgent_tickets_count': ServiceTicket.objects.filter(
            Q(assigned_engineers__isnull=True) | Q(priority__in=['high', 'urgent']),
            status__in=['open', 'in_progress']
        ).count(),
        'active_amc_count': AMCContract.objects.filter(status='active').count(),
        'expiring_amc_count': AMCContract.objects.filter(
            end_date__gte=now.date(), end_date__lte=thirty_days_from_now.date(), status='active'
        ).count(),
        # Project & Purchase
        'active_projects_count': active_projects_count,
        'items_to_purchase_count': items_to_purchase_count,
        'open_supplier_po_count': SupplierPurchaseOrder.objects.filter(status__in=['draft', 'sent', 'confirmed']).count(),
        # Store
        'low_stock_count': low_stock_count,
    }
