"""The NOA ERP admin dashboard: a registry of cards, resolved per user.

Wired in via UNFOLD['DASHBOARD_CALLBACK'] in settings.

What a user sees is decided in three layers, in this order:

1. **Permission** - a card declares the Django permission its data needs. If the
   user doesn't hold it, the card does not exist for them. This is a hard floor:
   no preset and no personal customisation can put it back.
2. **Role preset** - every card lists the departments it belongs to, so a store
   keeper's dashboard opens on stock and a sales user's opens on the pipeline,
   with no setup. Department comes from the user's role group ("Store Department
   - Data Entry" -> store).
3. **Personal choice** - once a user customises their dashboard, their own
   selection and ordering wins over the preset. Stored per user in
   DashboardPreference.

Colour note, unchanged from the first build: red and green are never adjacent
marks in the same chart, because under deuteranopia they are near-identical. The
invoice ramp deliberately puts amber between them. Status colours are otherwise
reserved for tiles, where an icon and a label carry the meaning too.
"""

import json
from dataclasses import dataclass, field
from datetime import timedelta
from functools import cached_property
from typing import Callable

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from core.models import (
    AMCContract, Employee, Invoice, Project, PurchaseRequisitionItem,
    Quotation, ServiceTicket, StockItem, StockTransaction, SupplierPurchaseOrder,
)

# ── Palette ────────────────────────────────────────────────────────
# Validated against this theme's own surfaces (white / slate-900). The severity
# ramp passes CVD separation at worst-adjacent ΔE 11.3 precisely because AMBER
# separates RED from GREEN - do not reorder it.
RED = '#d03b3b'      # critical  - money at risk, breached SLA
AMBER = '#fab219'    # warning   - in progress, needs a nudge
GREEN = '#0ca30c'    # good      - settled, closed, healthy
GREY = '#898781'     # neutral   - draft / not started
BLUE = '#2a78d6'     # brand hue - magnitude comparisons (single-hue bars)


# ── Departments ────────────────────────────────────────────────────
# Role groups are named "<Department> - <Access level>", so the part before the
# dash is the department. Superusers are treated as Master (they see everything).
SALES, SERVICE, STORE, PURCHASE, PROJECT, HR, MASTER = (
    'sales', 'service', 'store', 'purchase', 'project', 'hr', 'master',
)

DEPARTMENT_LABELS = {
    SALES: 'Sales & CRM', SERVICE: 'Service', STORE: 'Store & Stock',
    PURCHASE: 'Purchase', PROJECT: 'Projects', HR: 'HR', MASTER: 'Master',
}

_GROUP_PREFIX_TO_DEPARTMENT = {
    'Sales & CRM': SALES,
    'Service Department': SERVICE,
    'Store Department': STORE,
    'Purchase Department': PURCHASE,
    'Project Department': PROJECT,
    'HR & Admin': HR,
    'Master': MASTER,
}


def department_for(user):
    """Which department preset this user opens on, or None if unrecognised."""
    if user.is_superuser:
        return MASTER
    group = getattr(user, 'role', None)
    if not group:
        return None
    return _GROUP_PREFIX_TO_DEPARTMENT.get(group.name.split(' - ')[0].strip())


# ── Widget registry ────────────────────────────────────────────────

@dataclass(frozen=True)
class Widget:
    key: str
    title: str
    kind: str                      # hero | tile | chart | meters
    build: Callable                # (DashboardData) -> dict payload
    permission: str = ''           # '' means everyone with admin access
    departments: tuple = field(default_factory=tuple)
    description: str = ''


WIDGETS: dict[str, Widget] = {}


def register(key, title, kind, permission='', departments=(), description=''):
    def wrap(fn):
        WIDGETS[key] = Widget(
            key=key, title=title, kind=kind, build=fn,
            permission=permission, departments=tuple(departments),
            description=description,
        )
        return fn
    return wrap


def widgets_for(user):
    """Every card this user is permitted to see, registry order."""
    return [w for w in WIDGETS.values() if not w.permission or user.has_perm(w.permission)]


def default_keys_for(user):
    """The role preset: cards belonging to the user's department.

    Falls back to everything they're allowed to see, so a user whose group we
    don't recognise still gets a working dashboard rather than a blank one.
    """
    allowed = widgets_for(user)
    dept = department_for(user)
    if dept:
        preset = [w.key for w in allowed if dept in w.departments]
        if preset:
            return preset
    return [w.key for w in allowed]


def resolve_widgets(user):
    """The user's actual dashboard: their choice if set, else the role preset.

    Permission is re-applied over the stored selection, so a card keeps
    disappearing correctly if someone's access is revoked after they chose it.
    """
    allowed = {w.key: w for w in widgets_for(user)}
    preference = getattr(user, 'dashboard_preference', None)
    keys = (preference.widgets if preference and preference.widgets
            else default_keys_for(user))
    return [allowed[key] for key in keys if key in allowed]


# ── Shared data bag ────────────────────────────────────────────────

class DashboardData:
    """Figures shared across cards, each computed at most once per request."""

    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.now = timezone.now()
        self.today = timezone.localdate()
        self.in_30_days = self.today + timedelta(days=30)

    def url(self, name, query=''):
        return reverse(name) + query

    # -- invoices -------------------------------------------------
    @cached_property
    def open_invoices(self):
        # Invoice totals are computed in Python from line items rather than
        # stored on the row, so this has to walk the objects; prefetching keeps
        # it to three queries. If invoice volume grows large, denormalise a
        # total column onto Invoice and aggregate in SQL instead.
        return list(
            Invoice.objects.filter(status__in=['unpaid', 'partial'])
            .prefetch_related('items', 'payments')
        )

    @cached_property
    def outstanding(self):
        return sum(inv.get_balance_due() for inv in self.open_invoices)

    @cached_property
    def overdue_invoices(self):
        return [i for i in self.open_invoices if i.due_date and i.due_date < self.today]

    @cached_property
    def overdue_value(self):
        return sum(inv.get_balance_due() for inv in self.overdue_invoices)

    # -- stock ----------------------------------------------------
    @cached_property
    def active_stock_items(self):
        return list(StockItem.objects.filter(is_active=True))

    @cached_property
    def low_stock(self):
        return [i for i in self.active_stock_items
                if i.get_stock_balance() <= i.reorder_level]

    # -- service --------------------------------------------------
    @cached_property
    def open_tickets(self):
        return ServiceTicket.objects.filter(
            status__in=['open', 'assigned', 'in_progress']).count()

    @cached_property
    def urgent_tickets(self):
        return ServiceTicket.objects.filter(
            Q(assigned_engineers__isnull=True) | Q(priority__in=['high', 'urgent']),
            status__in=['open', 'in_progress'],
        ).distinct().count()

    @cached_property
    def expiring_amc(self):
        return AMCContract.objects.filter(
            status='active', end_date__gte=self.today, end_date__lte=self.in_30_days,
        ).count()

    # -- sales ----------------------------------------------------
    @cached_property
    def open_inquiries(self):
        from sales.models import SalesInquiry
        return SalesInquiry.objects.exclude(status__in=['won', 'lost']).count()

    @cached_property
    def pending_quotations(self):
        return Quotation.objects.filter(status__in=['draft', 'sent']).count()

    # -- projects / purchase --------------------------------------
    @cached_property
    def active_projects(self):
        return Project.objects.exclude(status__in=['completed', 'cancelled']).count()

    @cached_property
    def items_to_purchase(self):
        return PurchaseRequisitionItem.objects.filter(
            status__in=['pending', 'ordered']).count()

    @cached_property
    def open_supplier_pos(self):
        return SupplierPurchaseOrder.objects.filter(
            status__in=['draft', 'sent', 'confirmed']).count()


# ── Formatting helpers ─────────────────────────────────────────────

_BAR_OPTIONS = {
    'indexAxis': 'y',
    'responsive': True,
    'maintainAspectRatio': False,
    'plugins': {'legend': {'display': False}, 'tooltip': {'enabled': True}},
    'scales': {
        'x': {'beginAtZero': True, 'border': {'display': False},
              'grid': {'color': 'rgba(148,163,184,0.16)'},
              'ticks': {'precision': 0, 'color': '#898781'}},
        'y': {'border': {'display': False}, 'grid': {'display': False},
              'ticks': {'color': '#898781'}},
    },
}


def bar_chart(labels, values, colors, legend=()):
    """Chart.js payload for a horizontal bar chart.

    Unfold's chart component JSON.parses the data-value attribute, so both the
    data and the options travel as JSON strings.
    """
    return {
        'data': json.dumps({
            'labels': labels,
            'datasets': [{
                'data': values, 'backgroundColor': colors,
                'borderRadius': 4, 'borderWidth': 0, 'barPercentage': 0.65,
            }],
        }),
        'options': json.dumps(_BAR_OPTIONS),
        'legend': legend,
    }


def tile(label, value, url, icon, tone='neutral', hint=''):
    """One KPI stat tile. The icon and label carry the meaning, so the tone
    colour is reinforcement rather than the only cue."""
    return {'label': label, 'value': value, 'url': url,
            'icon': icon, 'tone': tone, 'hint': hint}


def meter(label, numerator, denominator, detail):
    if not denominator:
        return {'label': label, 'pct': None, 'detail': 'No data yet', 'tone': 'neutral'}
    pct = round((numerator / denominator) * 100)
    tone = 'good' if pct >= 70 else 'warning' if pct >= 40 else 'critical'
    return {'label': label, 'pct': pct, 'detail': detail, 'tone': tone}


def money(amount):
    """Compact Indian-format money label, e.g. 12.4 L / 3.2 Cr."""
    amount = float(amount or 0)
    if amount >= 10_000_000:
        return f'₹{amount / 10_000_000:.2f} Cr'
    if amount >= 100_000:
        return f'₹{amount / 100_000:.2f} L'
    if amount >= 1_000:
        return f'₹{amount / 1_000:.1f} K'
    return f'₹{amount:,.0f}'


# ── The cards ──────────────────────────────────────────────────────

@register('hero_receivables', 'Outstanding receivables', 'hero',
          permission='sales.view_salesinvoice', departments=(SALES, MASTER),
          description='Total unpaid balance, with the overdue portion called out.')
def _hero_receivables(d):
    return {
        'label': 'Outstanding receivables',
        'value': money(d.outstanding),
        'detail': (f'{len(d.overdue_invoices)} invoice(s) overdue · '
                   f'{money(d.overdue_value)} past due'
                   if d.overdue_invoices else 'Nothing past due'),
        'tone': 'critical' if d.overdue_invoices else 'good',
        'url': d.url('admin:sales_salesinvoice_changelist', '?status__exact=unpaid'),
    }


@register('tile_overdue_invoices', 'Overdue invoices', 'tile',
          permission='sales.view_salesinvoice', departments=(SALES, MASTER),
          description='Invoices past their due date and still unpaid.')
def _tile_overdue(d):
    return tile('Overdue invoices', len(d.overdue_invoices),
                d.url('admin:sales_salesinvoice_changelist', '?status__exact=unpaid'),
                'running_with_errors', 'critical', money(d.overdue_value) + ' past due')


@register('tile_open_inquiries', 'Open inquiries', 'tile',
          permission='sales.view_salesinquiry', departments=(SALES,),
          description='Inquiries not yet won or lost.')
def _tile_inquiries(d):
    return tile('Open inquiries', d.open_inquiries,
                d.url('admin:sales_salesinquiry_changelist'),
                'contact_support', 'neutral',
                f'{d.pending_quotations} quotations pending')


@register('tile_pending_quotations', 'Pending quotations', 'tile',
          permission='sales.view_salesquotation', departments=(SALES,),
          description='Quotations still in draft or awaiting a customer decision.')
def _tile_quotations(d):
    return tile('Pending quotations', d.pending_quotations,
                d.url('admin:sales_salesquotation_changelist'),
                'request_quote', 'warning' if d.pending_quotations else 'good',
                'draft or sent')


@register('tile_urgent_tickets', 'Urgent / unassigned tickets', 'tile',
          permission='service.view_serviceserviceticket', departments=(SERVICE, MASTER),
          description='Open tickets that are high priority or have no engineer.')
def _tile_urgent(d):
    return tile('Urgent / unassigned tickets', d.urgent_tickets,
                d.url('admin:service_serviceserviceticket_changelist',
                      '?priority__in=high,urgent&status__in=open,in_progress'),
                'priority_high', 'critical' if d.urgent_tickets else 'good',
                f'of {d.open_tickets} open tickets')


@register('tile_open_tickets', 'Open service tickets', 'tile',
          permission='service.view_serviceserviceticket', departments=(SERVICE,),
          description='Every ticket not yet resolved or closed.')
def _tile_open_tickets(d):
    return tile('Open service tickets', d.open_tickets,
                d.url('admin:service_serviceserviceticket_changelist',
                      '?status__in=open,assigned,in_progress'),
                'build', 'neutral', 'open, assigned or in progress')


@register('tile_amc_expiring', 'AMC expiring in 30 days', 'tile',
          permission='service.view_serviceamccontract', departments=(SERVICE,),
          description='Active contracts inside the renewal window.')
def _tile_amc(d):
    return tile('AMC expiring in 30 days', d.expiring_amc,
                d.url('admin:service_serviceamccontract_changelist',
                      '?status__exact=active'),
                'event_repeat', 'warning' if d.expiring_amc else 'good',
                'renewal window')


@register('tile_low_stock', 'Low stock items', 'tile',
          permission='store.view_storestockitem', departments=(STORE, MASTER),
          description='Active items at or below their reorder level.')
def _tile_low_stock(d):
    return tile('Low stock items', len(d.low_stock),
                d.url('admin:store_storestockitem_changelist'),
                'inventory_2', 'warning' if d.low_stock else 'good',
                f'of {len(d.active_stock_items)} active items')


@register('tile_pending_returnables', 'Pending returnables', 'tile',
          permission='store.view_pendingreturnableitems', departments=(STORE,),
          description='Returnable items issued out and not yet returned.')
def _tile_returnables(d):
    count = StockTransaction.objects.filter(
        transaction_type='issue', stock_item__is_returnable=True).count()
    return tile('Pending returnables', count,
                d.url('admin:store_pendingreturnableitems_changelist'),
                'assignment_return', 'warning' if count else 'good',
                'issued, awaiting return')


@register('tile_items_to_purchase', 'Items to purchase', 'tile',
          permission='purchase.view_itemstopurchase',
          departments=(PURCHASE, PROJECT),
          description='Requisition lines still pending or on order.')
def _tile_to_purchase(d):
    return tile('Items to purchase', d.items_to_purchase,
                d.url('admin:purchase_itemstopurchase_changelist'),
                'shopping_bag', 'warning' if d.items_to_purchase else 'good',
                'pending or ordered')


@register('tile_open_supplier_pos', 'Open supplier POs', 'tile',
          permission='purchase.view_supplierpurchaseorder', departments=(PURCHASE,),
          description='Purchase orders raised but not yet received.')
def _tile_supplier_pos(d):
    return tile('Open supplier POs', d.open_supplier_pos,
                d.url('admin:purchase_supplierpurchaseorder_changelist'),
                'local_shipping', 'neutral', 'draft, sent or confirmed')


@register('tile_active_projects', 'Active projects', 'tile',
          permission='project.view_project', departments=(PROJECT, MASTER),
          description='Projects not yet completed or cancelled.')
def _tile_projects(d):
    return tile('Active projects', d.active_projects,
                d.url('admin:project_project_changelist'),
                'workspaces', 'neutral', f'{d.items_to_purchase} items to purchase')


@register('tile_headcount', 'Employees on roll', 'tile',
          permission='hr.view_hremployee', departments=(HR,),
          description='Active employee headcount.')
def _tile_headcount(d):
    count = Employee.objects.filter(status='active').count()
    return tile('Employees on roll', count,
                d.url('admin:hr_hremployee_changelist'),
                'badge', 'neutral', 'active staff')


@register('tile_products', 'Products in catalogue', 'tile',
          permission='inventory.view_inventoryproduct', departments=(MASTER,),
          description='Size of the sellable product catalogue.')
def _tile_products(d):
    from core.models import Product
    count = Product.objects.count()
    return tile('Products in catalogue', count,
                d.url('admin:inventory_inventoryproduct_changelist'),
                'category', 'neutral', 'master catalogue')


@register('tile_suppliers', 'Active suppliers', 'tile',
          permission='core.view_supplier', departments=(MASTER, PURCHASE),
          description='Suppliers available to raise purchase orders against.')
def _tile_suppliers(d):
    from core.models import Supplier
    count = Supplier.objects.filter(is_active=True).count()
    return tile('Active suppliers', count,
                d.url('admin:core_supplier_changelist'),
                'store', 'neutral', 'available for POs')


@register('tile_users', 'User accounts', 'tile',
          permission='core.view_user', departments=(MASTER,),
          description='Active logins across all roles.')
def _tile_users(d):
    from core.models import User
    total = User.objects.filter(is_active=True).count()
    unassigned = User.objects.filter(is_active=True, role__isnull=True).count()
    return tile('User accounts', total,
                d.url('admin:core_user_changelist'),
                'manage_accounts', 'warning' if unassigned else 'neutral',
                f'{unassigned} without a role' if unassigned else 'all roles assigned')


@register('chart_workload', 'Open workload by department', 'chart',
          departments=(MASTER, SERVICE, SALES, STORE, PURCHASE, PROJECT, HR),
          description='Where the open work is sitting, across the departments you can see.')
def _chart_workload(d):
    # Single hue: the job is comparing magnitude, and the department names on
    # the axis already carry identity.
    #
    # The card itself needs no permission, so the BARS carry the check instead -
    # otherwise a store user would read the sales pipeline volume off a chart
    # they were never granted. A viewer only ever sees the departments they hold
    # a view permission for, and the card drops out below two bars, where a
    # comparison stops meaning anything.
    candidates = [
        ('Sales & CRM', 'sales.view_salesinquiry',
         d.open_inquiries + d.pending_quotations),
        ('Service', 'service.view_serviceserviceticket', d.open_tickets),
        ('Projects', 'project.view_project', d.active_projects),
        ('Purchase', 'purchase.view_itemstopurchase', d.items_to_purchase),
        ('Store', 'store.view_storestockitem', len(d.low_stock)),
    ]
    visible = [(label, value) for label, perm, value in candidates
               if d.user.has_perm(perm)]
    if len(visible) < 2:
        return None

    return bar_chart(
        [label for label, _ in visible],
        [value for _, value in visible],
        [BLUE] * len(visible),
    )


@register('chart_invoices', 'Invoices by status', 'chart',
          permission='sales.view_salesinvoice', departments=(SALES, MASTER),
          description='Billing split across unpaid, part-paid, paid and draft.')
def _chart_invoices(d):
    # Invoices carry real polarity (paid vs at-risk), so this one earns the
    # status ramp. Order is deliberate: amber sits between red and green.
    return bar_chart(
        ['Unpaid', 'Partially paid', 'Fully paid', 'Draft'],
        [Invoice.objects.filter(status='unpaid').count(),
         Invoice.objects.filter(status='partial').count(),
         Invoice.objects.filter(status='paid').count(),
         Invoice.objects.filter(status='draft').count()],
        [RED, AMBER, GREEN, GREY],
        legend=(('Unpaid', RED), ('Partially paid', AMBER),
                ('Fully paid', GREEN), ('Draft', GREY)),
    )


@register('meters_departments', 'Department performance', 'meters',
          departments=(MASTER, SALES, SERVICE, STORE, PURCHASE, PROJECT),
          description='Completion rate for the departments you can see.')
def _meters(d):
    # Same reasoning as the workload chart: no permission guards the card, so
    # each ROW carries its own, and a viewer only sees departments they hold a
    # view permission for.
    rows = []

    if d.user.has_perm('sales.view_salesquotation'):
        total = Quotation.objects.count()
        accepted = Quotation.objects.filter(status='accepted').count()
        rows.append(meter('Sales & CRM', accepted, total,
                          f'{accepted} of {total} quotations accepted'))

    if d.user.has_perm('service.view_serviceserviceticket'):
        total = ServiceTicket.objects.count()
        resolved = ServiceTicket.objects.filter(status__in=['resolved', 'closed']).count()
        rows.append(meter('Service', resolved, total,
                          f'{resolved} of {total} tickets resolved'))

    if d.user.has_perm('project.view_project'):
        total = Project.objects.count()
        done = Project.objects.filter(status='completed').count()
        rows.append(meter('Projects', done, total,
                          f'{done} of {total} projects completed'))

    if d.user.has_perm('purchase.view_supplierpurchaseorder'):
        total = SupplierPurchaseOrder.objects.exclude(status='cancelled').count()
        received = SupplierPurchaseOrder.objects.filter(status='received').count()
        rows.append(meter('Purchase', received, total,
                          f'{received} of {total} purchase orders received'))

    if d.user.has_perm('store.view_storestockitem'):
        active = len(d.active_stock_items)
        healthy = active - len(d.low_stock)
        rows.append(meter('Store', healthy, active,
                          f'{healthy} of {active} items at healthy stock'))

    return rows or None


# ── Entry point ────────────────────────────────────────────────────

def dashboard_callback(request, context):
    data = DashboardData(request)
    resolved = resolve_widgets(request.user)

    cards = []
    for widget in resolved:
        # A card may return None to withdraw itself - the workload chart and the
        # performance meters do this when the viewer's permissions leave them
        # with nothing worth showing. Rendering an empty frame would read as a
        # broken card, so drop it instead.
        payload = widget.build(data)
        if payload is None:
            continue
        cards.append({
            'key': widget.key,
            'kind': widget.kind,
            'title': widget.title,
            'payload': payload,
        })

    department = department_for(request.user)
    context.update({
        'cards': cards,
        'hero_card': next((c for c in cards if c['kind'] == 'hero'), None),
        'tile_cards': [c for c in cards if c['kind'] == 'tile'],
        'panel_cards': [c for c in cards if c['kind'] in ('chart', 'meters')],
        'dashboard_department': DEPARTMENT_LABELS.get(department, ''),
        'dashboard_customize_url': reverse('dashboard_customize'),
        'dashboard_is_customised': bool(
            getattr(request.user, 'dashboard_preference', None)
            and request.user.dashboard_preference.widgets
        ),
    })
    return context
