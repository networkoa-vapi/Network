"""Read-only health check for a NOA ERP deployment.

Run this after pulling a new version and applying migrations, to confirm the
install is sound BEFORE anyone relies on it. It is safe to run against a
production database: it only reads. It never creates, modifies or deletes a
single row, and it deliberately does not use the Django test client, because
logging a user in would write a session row.

    python scripts/verify_deployment.py

Exit code 0 means everything checked out; 1 means at least one FAIL that needs
looking at before the deployment is trusted.

The headline check is the last one. Every hand-declared sidebar entry and every
dashboard card is gated on a Django permission, and those permissions live on the
PROXY models (sales.view_salesinvoice), never on the concrete core models
(core.view_invoice) that the role groups are never granted. Guarding on the wrong
one hides the whole navigation from ordinary staff while leaving it perfect for
superusers, who bypass permission checks entirely. That bug is invisible unless
you look at what a real staff user resolves to - which is what this does.
"""

import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noa_erp.settings')
django.setup()

from django.conf import settings  # noqa: E402
from django.db.migrations.executor import MigrationExecutor  # noqa: E402
from django.db import connection  # noqa: E402

failures = []
warnings = []


def ok(msg):
    print(f'  PASS  {msg}')


def fail(msg):
    print(f'  FAIL  {msg}')
    failures.append(msg)


def warn(msg):
    print(f'  WARN  {msg}')
    warnings.append(msg)


class _Request:
    """Just enough of a request for the sidebar permission callables."""

    def __init__(self, user):
        self.user = user


print('\n=== 1. Dependencies ===')
try:
    import unfold  # noqa: F401
    ok(f'django-unfold importable (Django {django.get_version()})')
except ImportError:
    fail('django-unfold is NOT installed - run: pip install -r requirements.txt')
    print('\nCannot continue without it.')
    sys.exit(1)

print('\n=== 2. Migrations ===')
executor = MigrationExecutor(connection)
targets = executor.loader.graph.leaf_nodes()
plan = executor.migration_plan(targets)
if plan:
    fail(f'{len(plan)} migration(s) NOT applied - run: python manage.py migrate')
    for migration, _ in plan[:10]:
        print(f'        pending: {migration.app_label}.{migration.name}')
else:
    ok('all migrations applied')

try:
    from core.models import DashboardPreference
    DashboardPreference.objects.exists()      # read-only touch
    ok('dashboard preference table present and readable')
except Exception as exc:                       # noqa: BLE001
    fail(f'dashboard preference table missing or unreadable: {exc}')

print('\n=== 3. Data still intact ===')
from core.models import (  # noqa: E402
    CustomerProfile, Employee, Invoice, Quotation, ServiceTicket, StockItem, User,
)

counts = {
    'users': User.objects.count(),
    'customers': CustomerProfile.objects.count(),
    'quotations': Quotation.objects.count(),
    'invoices': Invoice.objects.count(),
    'service tickets': ServiceTicket.objects.count(),
    'stock items': StockItem.objects.count(),
    'employees': Employee.objects.count(),
}
for label, count in counts.items():
    print(f'        {label:16} {count}')
ok('business tables readable')

demo_users = User.objects.filter(username__startswith='demo_').count()
if demo_users:
    warn(f'{demo_users} demo user(s) present (username starts with "demo_") - '
         'if this is the production database, seed_demo was run here at some point')
else:
    ok('no demo data in this database')

print('\n=== 4. Dashboard cards ===')
from core.dashboard import WIDGETS, department_for, resolve_widgets  # noqa: E402

ok(f'{len(WIDGETS)} dashboard cards registered')

print('\n=== 5. Permission strings actually exist ===')
from django.contrib.auth.models import Permission  # noqa: E402

real_perms = {f'{p.content_type.app_label}.{p.codename}'
              for p in Permission.objects.select_related('content_type')}

declared = {w.permission for w in WIDGETS.values() if w.permission}
missing = sorted(p for p in declared if p not in real_perms)
if missing:
    for perm in missing:
        fail(f'dashboard card requires "{perm}", which does not exist')
else:
    ok(f'all {len(declared)} card permissions exist')

print('\n=== 6. What real staff users actually see ===')
print('        (the check that catches an empty sidebar)\n')

nav_groups = settings.UNFOLD.get('SIDEBAR', {}).get('navigation', [])
total_nav_items = sum(len(g.get('items', [])) for g in nav_groups)
print(f'        sidebar declares {total_nav_items} entries across '
      f'{len(nav_groups)} groups\n')

staff = (User.objects.filter(is_active=True, is_staff=True)
         .select_related('role').order_by('username'))

if not staff.exists():
    warn('no active staff users found to check')

blind = []
for user in staff:
    request = _Request(user)

    visible = 0
    for group in nav_groups:
        for item in group.get('items', []):
            check = item.get('permission')
            try:
                if check is None or check(request):
                    visible += 1
            except Exception:                      # noqa: BLE001, S110
                pass

    cards = len(resolve_widgets(user))
    dept = department_for(user) or '-'
    role = user.role.name if user.role else '(no role assigned)'
    flag = 'superuser' if user.is_superuser else dept

    line = (f'        {user.username:22} {flag:10} '
            f'sidebar {visible:2}/{total_nav_items}   cards {cards:2}   {role}')
    print(line)

    if not user.is_superuser:
        if visible == 0:
            blind.append(user.username)
        if user.role is None:
            warn(f'{user.username} is staff but has no role assigned')

print()
if blind:
    fail(f'{len(blind)} non-superuser staff would see an EMPTY sidebar: '
         f'{", ".join(blind)}')
    print('        This is the proxy-permission bug. Sidebar and dashboard guards')
    print('        must name the proxy model (sales.view_salesinvoice), not the')
    print('        core model (core.view_invoice), which role groups never hold.')
elif staff.filter(is_superuser=False).exists():
    ok('every non-superuser staff member resolves to a usable sidebar')
else:
    warn('only superusers exist - a superuser bypasses every permission check, so '
         'this run proves nothing about ordinary staff. Re-run once a real staff '
         'account exists.')

print('\n=== 7. Portal role groups ===')
from django.contrib.auth.models import Group  # noqa: E402

for name in ('Customer', 'Engineer'):
    if Group.objects.filter(name=name).exists():
        ok(f'group "{name}" exists')
    else:
        warn(f'group "{name}" is missing - the {name.lower()} portal login will '
             f'not work until it is created')

print('\n' + '=' * 60)
print(f'{len(failures)} failure(s), {len(warnings)} warning(s)')
for f in failures:
    print(f'  FAIL  {f}')
for w in warnings:
    print(f'  WARN  {w}')
print('=' * 60)
print('This script only read from the database. Nothing was modified.')

sys.exit(1 if failures else 0)
