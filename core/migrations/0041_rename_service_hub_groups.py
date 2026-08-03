"""
"Service Hub" was renamed to "Service Department" for consistency with the other
department names (Project Department, Store Department, Purchase Department, etc.).
Renames the permission Groups created by 0036 so existing installs pick up the new
name instead of ending up with duplicates.
"""
from django.db import migrations

RENAMES = [
    ('Service Hub - Full Access', 'Service Department - Full Access'),
    ('Service Hub - Data Entry', 'Service Department - Data Entry'),
    ('Service Hub - View Only', 'Service Department - View Only'),
]


def rename_forwards(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for old_name, new_name in RENAMES:
        Group.objects.filter(name=old_name).update(name=new_name)


def rename_backwards(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for old_name, new_name in RENAMES:
        Group.objects.filter(name=new_name).update(name=old_name)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_offerletter_conveyance_allowance'),
    ]

    operations = [
        migrations.RunPython(rename_forwards, rename_backwards),
    ]
