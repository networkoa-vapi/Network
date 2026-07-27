from django import template
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

# Import models
from sales.models import SalesInquiry
from core.models import CustomerProfile, ServiceTicket, AMCContract, Invoice

register = template.Library()

@register.inclusion_tag('admin/kpi_dashboard.html', takes_context=True)
def render_dashboard_kpis(context):
    now = timezone.now()
    thirty_days_from_now = now + timedelta(days=30)
    
    # 1. KPIs
    # Open Sales Inquiries (assuming status 'draft' or 'open' - from previous check it has 'status')
    open_inquiries_count = SalesInquiry.objects.exclude(status__in=['converted', 'lost']).count()
    
    # Active Customers
    active_customers_count = CustomerProfile.objects.count()
    
    # Open Support Tickets
    open_tickets_count = ServiceTicket.objects.filter(status__in=['open', 'assigned', 'in_progress']).count()
    
    # Active AMC Contracts
    active_amc_count = AMCContract.objects.filter(status='active').count()
    
    # 2. Tracking Control Points
    
    # Unassigned or Urgent Tickets
    actionable_tickets = ServiceTicket.objects.filter(
        Q(assigned_engineer__isnull=True) | Q(priority__in=['high', 'urgent']),
        status__in=['open', 'in_progress']
    ).order_by('-created_at')[:5]
    
    # Expiring AMC Contracts (next 30 days)
    expiring_contracts = AMCContract.objects.filter(
        end_date__gte=now.date(),
        end_date__lte=thirty_days_from_now.date(),
        status='active'
    ).order_by('end_date')[:5]
    
    # Overdue Invoices
    overdue_invoices = Invoice.objects.filter(
        status='unpaid',
        due_date__lt=now.date()
    ).order_by('due_date')[:5]
    
    # Pending Inquiries (recent)
    pending_inquiries = SalesInquiry.objects.exclude(
        status__in=['converted', 'lost']
    ).order_by('-created_at')[:5]
    
    return {
        'open_inquiries_count': open_inquiries_count,
        'active_customers_count': active_customers_count,
        'open_tickets_count': open_tickets_count,
        'active_amc_count': active_amc_count,
        'actionable_tickets': actionable_tickets,
        'expiring_contracts': expiring_contracts,
        'overdue_invoices': overdue_invoices,
        'pending_inquiries': pending_inquiries,
    }
