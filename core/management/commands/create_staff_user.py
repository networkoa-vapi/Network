"""Create an internal staff user, wired to a department role group correctly.

    python manage.py create_staff_user sadik --group "Store Department - Full Access"

Why this exists rather than "just add a user in the admin": a working staff account
needs its department group in TWO places, and setting only one leaves an account
that looks fine on the user form and is useless in practice.

    user.role    -> which dashboard preset they get
    user.groups  -> the permissions they actually hold

Set only `role` and the user has a department but no permissions, so their sidebar
and dashboard come up EMPTY - indistinguishable from the proxy-permission bug this
project already had once. This command always sets both, and then prints what the
new account actually resolves to so you can see it worked.

No password is set here, deliberately. Passing one on the command line would leak
it into shell history, and prompting would hang when this is run by an automation
or agent. The account is created with an unusable password and cannot be logged
into until you set one from the admin UI (Users -> pick the user -> password form),
which is also where it gets recorded properly.

Safe to run against a live database: it only ever adds or repairs the single named
account, and it never touches business records.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.dashboard import department_for, resolve_widgets
from core.models import User


class Command(BaseCommand):
    help = 'Create or repair an internal staff user attached to a department role group.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument(
            '--group', default='',
            help='Role group name, e.g. "Store Department - Full Access". '
                 'Required unless --superuser is given.',
        )
        parser.add_argument('--first', default='', help='First name.')
        parser.add_argument('--last', default='', help='Last name.')
        parser.add_argument('--email', default='', help='Email address.')
        parser.add_argument(
            '--superuser', action='store_true',
            help='Make this a superuser (full access, bypasses all permission checks).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username'].strip()
        group_name = options['group'].strip()
        is_superuser = options['superuser']

        if not group_name and not is_superuser:
            raise CommandError(
                'Give --group (a role group name), or --superuser for a full-access '
                'account.\n\nAvailable groups:\n  ' + self._group_list()
            )

        group = None
        if group_name:
            group = Group.objects.filter(name=group_name).first()
            if not group:
                raise CommandError(
                    f'No role group named "{group_name}".\n\nAvailable groups:\n  '
                    + self._group_list()
                )

        user = User.objects.filter(username=username).first()
        created = user is None

        if created:
            user = User(username=username)
            # Unusable password: the account exists but cannot be signed into until
            # a password is set from the admin. Nothing secret passes through here.
            user.set_unusable_password()

        user.first_name = options['first'] or user.first_name
        user.last_name = options['last'] or user.last_name
        user.email = options['email'] or user.email
        user.is_active = True
        user.is_staff = True
        if is_superuser:
            user.is_superuser = True
        if group:
            user.role = group          # drives the dashboard preset
        user.save()

        if group:
            user.groups.add(group)     # drives the actual permissions
            user.save()

        # Re-fetch so the permission cache reflects the group we just attached.
        user = User.objects.get(pk=user.pk)

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'{"Created" if created else "Updated"} staff user "{username}"')
        )
        self.stdout.write(f'  name        {user.get_full_name() or "(not set)"}')
        self.stdout.write(f'  email       {user.email or "(not set)"}')
        self.stdout.write(f'  role group  {group.name if group else "(none)"}')
        self.stdout.write(f'  superuser   {"yes" if user.is_superuser else "no"}')

        self._report_access(user)

        if created:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                'No password is set, so this account cannot sign in yet.\n'
                'Set one in the admin: Users -> ' + username + ' -> "this form" link\n'
                'in the password field. Do not set passwords from the command line.'
            ))

    def _group_list(self):
        names = Group.objects.order_by('name').values_list('name', flat=True)
        return '\n  '.join(names) if names else '(none defined)'

    def _report_access(self, user):
        """Show what this account actually resolves to - the real proof it works."""
        from django.conf import settings

        class _Request:
            pass

        request = _Request()
        request.user = user

        nav_groups = settings.UNFOLD.get('SIDEBAR', {}).get('navigation', [])
        all_items = [item for g in nav_groups for item in g.get('items', [])]

        # Dashboard and Reports Center carry no permission, so they show for anyone
        # who can reach the admin. Counting them would report "2 entries visible"
        # for an account that can actually open nothing, so module access is
        # measured only across the permission-guarded entries.
        guarded_total = sum(1 for item in all_items if item.get('permission') is not None)
        visible = 0
        visible_guarded = 0
        for item in all_items:
            check = item.get('permission')
            if check is None:
                visible += 1
                continue
            try:
                if check(request):
                    visible += 1
                    visible_guarded += 1
            except Exception:                           # noqa: BLE001, S110
                pass

        cards = len(resolve_widgets(user))
        department = department_for(user) or '(none)'

        self.stdout.write('')
        self.stdout.write('  What this account will see:')
        self.stdout.write(f'    department  {department}')
        self.stdout.write(f'    sidebar     {visible} of {len(all_items)} entries')
        self.stdout.write(f'    modules     {visible_guarded} of {guarded_total} '
                          f'(screens they can actually open)')
        self.stdout.write(f'    dashboard   {cards} cards')

        if visible_guarded == 0 and not user.is_superuser:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(
                '    NO MODULE ACCESS - this account can open nothing.\n'
                '    Only the permission-free entries (Dashboard, Reports Center)\n'
                '    would show. The role group holds no view permissions - check it\n'
                '    in the admin under Roles & Permissions before handing this over.'
            ))
