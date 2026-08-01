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
        _meter('Service Hub', 'service', resolved_tickets, total_tickets,
               f'{resolved_tickets} of {total_tickets} tickets resolved'),
        _meter('Project Department', 'project', completed_projects, total_projects,
               f'{completed_projects} of {total_projects} projects completed'),
        _meter('Purchase Department', 'purchase', received_po, total_po,
               f'{received_po} of {total_po} purchase orders received'),
        _meter('Store Department', 'store', healthy_stock_count, len(active_items),
               f'{healthy_stock_count} of {len(active_items)} items at healthy stock'),
    ]

    return {
        'performance_meters': performance_meters,
        # Sales
        'open_inquiries_count': SalesInquiry.objects.exclude(status__in=['won', 'lost']).count(),
        'pending_quotations_count': Quotation.objects.filter(status__in=['draft', 'sent']).count(),
        'active_sales_orders_count': SalesOrder.objects.exclude(status__in=['completed', 'cancelled']).count(),
        'active_customers_count': CustomerProfile.objects.count(),
        'overdue_invoices_count': Invoice.objects.filter(status='unpaid', due_date__lt=now.date()).count(),
        # Service
        'open_tickets_count': ServiceTicket.objects.filter(status__in=['open', 'assigned', 'in_progress']).count(),
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
        'active_projects_count': Project.objects.exclude(status__in=['completed', 'cancelled']).count(),
        'items_to_purchase_count': PurchaseRequisitionItem.objects.filter(status__in=['pending', 'ordered']).count(),
        'open_supplier_po_count': SupplierPurchaseOrder.objects.filter(status__in=['draft', 'sent', 'confirmed']).count(),
        # Store
        'low_stock_count': low_stock_count,
    }
