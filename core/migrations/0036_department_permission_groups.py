"""
Creates ready-to-use permission Groups, one per department x access level, so an
admin can assign a user "Sales & CRM - View Only" or "Store Department - Data Entry"
etc. directly, instead of hand-picking permissions for ~40 models one at a time.
A user can be added to as many of these as needed - e.g. "Sales & CRM - Full Access"
+ "Service Department - View Only" - mixing full/partial access per department freely.

Deliberately excludes the 'auth' app (User/Group/Permission management itself) -
that stays a superuser-only capability, not something any department group grants.
"""
from django.db import migrations
from django.db.models import Q

DEPARTMENTS = [
    ('Sales & CRM', ['sales']),
    ('Project Department', ['project']),
    ('Service Department', ['service']),
    ('Store Department', ['store']),
    ('Purchase Department', ['purchase']),
    ('HR & Admin', ['hr']),
    ('Master', ['core', 'inventory']),
]

LEVELS = [
    ('Full Access', ('add', 'change', 'delete', 'view')),
    ('Data Entry', ('add', 'view')),
    ('View Only', ('view',)),
]


def create_department_groups(apps, schema_editor):
    # post_migrate (which normally auto-creates each model's add/change/delete/view
    # permissions) only fires once the *entire* migrate run finishes - don't assume
    # it has already happened by the time this migration executes.
    from django.contrib.auth.management import create_permissions
    from django.apps import apps as global_apps

    for dept_label, app_labels in DEPARTMENTS:
        for app_label in app_labels:
            create_permissions(global_apps.get_app_config(app_label), verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    for dept_label, app_labels in DEPARTMENTS:
        ct_ids = list(ContentType.objects.filter(app_label__in=app_labels).values_list('id', flat=True))
        if not ct_ids:
            continue
        for level_label, actions in LEVELS:
            group, _ = Group.objects.get_or_create(name=f"{dept_label} - {level_label}")
            action_q = Q()
            for action in actions:
                action_q |= Q(codename__startswith=f'{action}_')
            perms = Permission.objects.filter(action_q, content_type_id__in=ct_ids)
            group.permissions.set(perms)


def remove_department_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    names = [f"{dept_label} - {level_label}" for dept_label, _ in DEPARTMENTS for level_label, _ in LEVELS]
    Group.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_employee_preferred_printer_employee_whatsapp_number'),
        ('sales', '0002_salesinvoiceseries_salesorder_salesorderseries_and_more'),
        ('project', '0001_initial'),
        ('service', '0004_serviceamccoverageitem'),
        ('store', '0005_pendingreturnableitems_refillentry_and_more'),
        ('purchase', '0002_supplierpurchaseorder'),
        ('hr', '0001_initial'),
        ('inventory', '0002_inventorydivision_and_more'),
    ]

    operations = [
        migrations.RunPython(create_department_groups, remove_department_groups),
    ]
