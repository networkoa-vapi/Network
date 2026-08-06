"""Seed a realistic cross-module dataset for demos and UI work.

The dashboard, charts and every changelist look empty on a fresh database, which
makes the system impossible to show to a prospect. This fills every module with
plausible, interlinked data - customers who raised inquiries that became
quotations, some of which became invoices that are variously paid, part-paid and
overdue; stock that has been received and issued until some items fall below
reorder level; tickets at every stage; AMCs about to expire.

Deterministic: the same seed produces the same dataset every run, so screenshots
and demos are reproducible.

    python manage.py seed_demo            # add demo data
    python manage.py seed_demo --reset    # remove previous demo data, then add

Everything it creates is tagged (users are prefixed 'demo_', other records carry
a DEMO_TAG marker in a notes/remarks field) so --reset can find and remove it
without touching real records.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import (
    AMCContract, Company, CustomerProfile, Division, Employee, Equipment,
    Godown, Inquiry, Invoice, InvoiceItem, InvoiceSeries, Payment, Product,
    ProductCategory, Project, PurchaseRequisition, PurchaseRequisitionItem,
    Quotation, QuotationItem, ServiceTicket, StockCategory, StockItem,
    StockTransaction, Supplier, SupplierPurchaseOrder, User,
)

DEMO_TAG = '[demo-data]'
USER_PREFIX = 'demo_'

BUSINESSES = [
    ('Sunrise Hospitality Pvt Ltd', 'Ahmedabad'),
    ('Meridian Tech Park', 'Gandhinagar'),
    ('Kalpataru Textiles', 'Surat'),
    ('Blue Orchid Hotels', 'Vadodara'),
    ('Nandan Healthcare', 'Rajkot'),
    ('Shreeji Logistics', 'Ahmedabad'),
    ('Aarav Foods & Beverages', 'Anand'),
    ('Vertex Business Centre', 'Ahmedabad'),
]

CONTACTS = [
    'Rakesh Mehta', 'Priya Shah', 'Imran Qureshi', 'Anita Desai',
    'Vikram Patel', 'Sneha Joshi', 'Farhan Shaikh', 'Deepak Rao',
]

ENGINEERS = [
    ('Nikhil', 'Bhatt', 'Senior Service Engineer'),
    ('Ravi', 'Chauhan', 'Service Engineer'),
    ('Sameer', 'Kapadia', 'Service Engineer'),
    ('Jyoti', 'Nair', 'Service Coordinator'),
]

SUPPLIERS = [
    'Voltas Distribution Ltd', 'Daikin Airconditioning India',
    'Havells Spares Depot', 'Copper Line Traders', 'Refrigerants Direct',
]

STOCK_SEED = [
    # (category, name, code, unit, reorder level)
    ('Spare Parts', 'Compressor 1.5 Ton Rotary', 'SP-COMP-15', 'nos', 5),
    ('Spare Parts', 'PCB Inverter Control Board', 'SP-PCB-INV', 'nos', 6),
    ('Spare Parts', 'Blower Motor Assembly', 'SP-BLW-01', 'nos', 4),
    ('Spare Parts', 'Capacitor 45uF', 'SP-CAP-45', 'nos', 20),
    ('Spare Parts', 'Thermostat Sensor', 'SP-THS-01', 'nos', 15),
    ('Consumables', 'R32 Refrigerant Gas', 'CN-GAS-R32', 'kg', 25),
    ('Consumables', 'R410A Refrigerant Gas', 'CN-GAS-410', 'kg', 20),
    ('Consumables', 'Copper Pipe 1/4 inch', 'CN-CU-025', 'ft', 200),
    ('Consumables', 'Copper Pipe 1/2 inch', 'CN-CU-050', 'ft', 150),
    ('Consumables', 'Insulation Sleeve', 'CN-INS-01', 'ft', 300),
    ('Consumables', 'Drain Pipe PVC', 'CN-DRN-01', 'ft', 250),
    ('Tools', 'Vacuum Pump', 'TL-VAC-01', 'nos', 2),
    ('Tools', 'Digital Manifold Gauge', 'TL-MAN-01', 'nos', 3),
    ('Tools', 'Flaring Tool Kit', 'TL-FLR-01', 'nos', 3),
    ('Installation Material', 'Wall Mounting Bracket', 'IM-BRK-01', 'nos', 30),
    ('Installation Material', 'Copper Lugs Pack', 'IM-LUG-01', 'box', 12),
]

PROBLEMS = [
    ('AC not cooling', 'Unit runs but no cooling. Suspect gas leak or compressor fault.'),
    ('Water leakage from indoor unit', 'Continuous dripping from the indoor unit onto the false ceiling.'),
    ('Unit not powering on', 'No display, no response from remote. Power supply checked at site.'),
    ('Excessive noise from outdoor unit', 'Loud rattling noise during operation, worse at night.'),
    ('Remote not responding', 'Remote replaced batteries, still no response from unit.'),
    ('Ice formation on coil', 'Visible ice build-up on the evaporator coil.'),
    ('Foul smell from vents', 'Musty odour when unit starts. Filters likely need service.'),
    ('Display showing error code', 'Panel shows E4 error and unit shuts down after 5 minutes.'),
]

PROJECT_NAMES = [
    'Central AC retrofit - Block B',
    'Ducted AC installation - new wing',
    'Cold room commissioning',
    'Server room precision cooling',
    'Cassette AC rollout - 12 units',
    'Chiller plant annual overhaul',
]


class Command(BaseCommand):
    help = 'Seed realistic interlinked demo data across every module.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Delete previously seeded demo data before seeding again.',
        )
        parser.add_argument(
            '--yes', action='store_true',
            help='Proceed even though the database already holds real business records.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.rng = random.Random(1337)
        self.today = timezone.localdate()

        # Guard rails. This command is in the repo, so it lands on every machine
        # that pulls - including ones running live business data. Neither mode may
        # touch real records by accident.
        has_demo = User.objects.filter(username__startswith=USER_PREFIX).exists()
        has_real = self._has_real_data()

        if options['reset'] and not has_demo:
            raise CommandError(
                'Refusing to run --reset: this database has no demo data in it '
                '(no users named "%s*"). There is nothing for the cleanup to remove, '
                'and running it anyway could only touch real records. '
                'Nothing was changed.' % USER_PREFIX
            )

        if has_real and not options['yes']:
            raise CommandError(
                'Refusing to seed: this database already holds real business records. '
                'seed_demo would add fictitious customers, quotations, invoices and '
                'stock alongside your live data. If that is genuinely what you want, '
                're-run with --yes. Nothing was changed.'
            )

        self.had_real_data = has_real

        if options['reset']:
            self._reset()

        company = Company.objects.order_by('pk').first()
        if not company:
            company = Company.objects.create(
                name='Network Office Automation', brand_name='NOA',
                contact_email='info@noa.com', contact_phone='9825000000',
            )
            self.stdout.write('created company')

        self.company = company

        products = self._products()
        customers = self._customers()
        engineers = self._engineers()
        self._inquiries(customers)
        quotations = self._quotations(customers, products)
        self._invoices(customers, products, quotations)
        equipment = self._equipment(customers, products)
        self._amc_contracts(customers, products)
        self._tickets(customers, equipment, engineers)
        self._staff_pm_tickets(engineers)
        stock_items, godowns = self._stock()
        projects = self._projects(customers)
        self._requisitions(projects, stock_items)
        self._suppliers_and_pos(projects)

        self.stdout.write(self.style.SUCCESS(
            '\nDemo data seeded. Run "python manage.py seed_demo --reset" to clear it.'
        ))

    # ── helpers ────────────────────────────────────────────────────

    def _log(self, label, count):
        self.stdout.write(f'  {label:<28} {count}')

    def _has_real_data(self):
        """True when the database holds business records this command didn't create.

        Everything seeded here hangs off a user named 'demo_*', so anything outside
        that set was put there by a person and must not be disturbed.
        """
        return (
            CustomerProfile.objects.exclude(user__username__startswith=USER_PREFIX).exists()
            or Invoice.objects.exclude(customer__user__username__startswith=USER_PREFIX).exists()
            or ServiceTicket.objects.exclude(customer__user__username__startswith=USER_PREFIX).exists()
            or StockTransaction.objects.exclude(remarks__contains=DEMO_TAG).exists()
        )

    def _reset(self):
        """Remove anything a previous run created.

        Deleting the demo users cascades to their customer profiles and, through
        those, to most transactional records. The remaining models are matched on
        their DEMO_TAG marker.
        """
        for model, field in (
            (StockTransaction, 'remarks'), (SupplierPurchaseOrder, 'remarks'),
            (PurchaseRequisition, 'remarks'), (Project, 'notes'),
            (StockItem, 'notes'), (Godown, 'location'),
            (Supplier, 'notes'), (Equipment, 'notes'),
            # Inquiry.customer_profile doesn't cascade, so deleting the demo users
            # leaves inquiries behind - they have to be matched on their own tag.
            (Inquiry, 'requirement'),
        ):
            deleted, _ = model.objects.filter(**{f'{field}__contains': DEMO_TAG}).delete()
            if deleted:
                self._log(f'removed {model.__name__}', deleted)

        deleted, _ = User.objects.filter(username__startswith=USER_PREFIX).delete()
        if deleted:
            self._log('removed demo users (cascade)', deleted)

        InvoiceSeries.objects.filter(name__contains='Demo').delete()

        # Stock categories carry no notes column, so they can only be matched by
        # name - and the names this command uses ("Spare Parts", "Consumables",
        # "Tools") are exactly what a real business would call its own categories.
        # Deleting by name is therefore only safe on a database with no real data
        # in it; anywhere else the empty leftovers are left alone rather than risk
        # removing someone's category.
        if self.had_real_data:
            self._log('kept StockCategory rows (real data present)', 0)
            return

        emptied = 0
        for category in StockCategory.objects.filter(name__in={c for c, *_ in STOCK_SEED}):
            if not StockItem.objects.filter(category=category).exists():
                category.delete()
                emptied += 1
        if emptied:
            self._log('removed empty StockCategory', emptied)

    def _products(self):
        products = list(Product.objects.all()[:40])
        if products:
            self._log('products (existing)', len(products))
            return products

        division, _ = Division.objects.get_or_create(company=self.company, name='Air Conditioning')
        category, _ = ProductCategory.objects.get_or_create(company=self.company, name='Room Air Conditioners')
        catalog = [
            ('Split AC 1.0 Ton 3 Star Inverter', 'AC-SPL-10-3S', 32990),
            ('Split AC 1.5 Ton 3 Star Inverter', 'AC-SPL-15-3S', 36990),
            ('Split AC 1.5 Ton 5 Star Inverter', 'AC-SPL-15-5S', 42990),
            ('Split AC 2.0 Ton 5 Star Inverter', 'AC-SPL-20-5S', 58990),
            ('Window AC 1.5 Ton 3 Star', 'AC-WIN-15-3S', 28990),
            ('Cassette AC 2.0 Ton', 'AC-CAS-20', 65000),
            ('Cassette AC 3.0 Ton', 'AC-CAS-30', 85000),
            ('Ducted Split AC 5.5 Ton', 'AC-DUC-55', 125000),
            ('Ducted Split AC 8.5 Ton', 'AC-DUC-85', 180000),
            ('Water Cooler 80L', 'WC-080', 34500),
            ('Deep Freezer 300L', 'DF-300', 41500),
            ('Air Purifier Commercial', 'AP-COM-01', 27500),
        ]
        for name, sku, price in catalog:
            products.append(Product.objects.create(
                company=self.company, division=division, category=category,
                name=name, sku=sku, base_price=Decimal(price),
            ))
        self._log('products created', len(products))
        return products

    def _customers(self):
        # The portal gates every customer page on user.role.name == 'Customer'
        # (core.views.is_customer), and no such group ships with the app - without
        # it these logins bounce straight back out of the portal.
        customer_group, created = Group.objects.get_or_create(name='Customer')
        if created:
            self._log('created "Customer" role group', 1)

        customers = []
        for i, (business, city) in enumerate(BUSINESSES):
            user = User.objects.create_user(
                username=f'{USER_PREFIX}cust{i + 1}',
                email=f'contact{i + 1}@{business.split()[0].lower()}.example.com',
                password='demo12345',
                first_name=CONTACTS[i].split()[0],
                last_name=CONTACTS[i].split()[1],
                company=self.company, role=customer_group,
            )
            customers.append(CustomerProfile.objects.create(
                company=self.company, user=user, business_name=business,
                gst_number=f'24ABCDE{1000 + i}F1Z{i}',
                billing_address=f'{100 + i * 7}, Industrial Estate, {city}, Gujarat',
                shipping_address=f'{100 + i * 7}, Industrial Estate, {city}, Gujarat',
            ))
        self._log('customers', len(customers))
        return customers

    def _engineers(self):
        # ServiceTicket.assigned_engineers carries
        # limit_choices_to={'user__role__name': 'Engineer'}, so an employee is only
        # offered in the admin's engineer picker when their role group is named
        # exactly "Engineer". That group doesn't ship with the app, so create it.
        engineer_group, created = Group.objects.get_or_create(name='Engineer')
        if created:
            self._log('created "Engineer" role group', 1)

        engineers = []
        for i, (first, last, designation) in enumerate(ENGINEERS):
            user = User.objects.create_user(
                username=f'{USER_PREFIX}eng{i + 1}',
                email=f'{first.lower()}.{last.lower()}@noa.example.com',
                password='demo12345', first_name=first, last_name=last,
                is_staff=True, company=self.company, role=engineer_group,
            )
            engineers.append(Employee.objects.create(
                user=user, company=self.company, employee_code=f'NOA-E{200 + i}',
                designation=designation, department='service',
                date_of_joining=self.today - timedelta(days=400 + i * 130),
                years_of_experience=Decimal(self.rng.randint(2, 14)),
                contact_number=f'98250{10000 + i}',
            ))
        self._log('engineers', len(engineers))
        return engineers

    def _inquiries(self, customers):
        statuses = ['new', 'new', 'contacted', 'contacted', 'quoted', 'quoted',
                    'quoted', 'won', 'won', 'lost', 'new', 'contacted', 'quoted', 'new']
        made = 0
        for i, status in enumerate(statuses):
            customer = customers[i % len(customers)]
            inquiry = Inquiry.objects.create(
                company=self.company, customer_profile=customer,
                name=customer.user.get_full_name(),
                phone=f'98{self.rng.randint(10000000, 99999999)}',
                email=customer.user.email,
                requirement=self.rng.choice([
                    'Requirement for 6 split ACs across two floors.',
                    'Looking for annual maintenance for 22 existing units.',
                    'Need a quote for cold room installation.',
                    'Replacement of 4 old window ACs with inverter splits.',
                    'Ducted AC for a new 2,400 sq ft office wing.',
                ]) + f' {DEMO_TAG}',
                status=status,
            )
            self._backdate(Inquiry, inquiry.pk, 'created_at', self.rng.randint(5, 120))
            made += 1
        self._log('inquiries', made)

    def _quotations(self, customers, products):
        # Weighted so the pipeline looks like a real one: more sent than accepted,
        # a few rejected, a couple still in draft.
        statuses = (['draft'] * 3) + (['sent'] * 7) + (['accepted'] * 7) + (['rejected'] * 3)
        quotations = []
        for i, status in enumerate(statuses):
            customer = customers[i % len(customers)]
            quote = Quotation.objects.create(
                company=self.company, customer=customer, status=status,
                valid_until=self.today + timedelta(days=self.rng.randint(5, 45)),
                terms_and_conditions='Prices valid for 30 days. Installation charged separately.',
            )
            for product in self.rng.sample(products, self.rng.randint(1, 4)):
                QuotationItem.objects.create(
                    quotation=quote, product=product,
                    quantity=self.rng.randint(1, 8),
                    unit_price=product.base_price,
                )
            self._backdate(Quotation, quote.pk, 'created_at', self.rng.randint(3, 90))
            quotations.append(quote)
        self._log('quotations', len(quotations))
        return quotations

    def _invoices(self, customers, products, quotations):
        series, _ = InvoiceSeries.objects.get_or_create(
            company=self.company, name='Demo Invoice Series',
            defaults={'prefix': 'NOA/INV/', 'next_number': 1},
        )
        # A spread that gives the dashboard something to say: real receivables,
        # a few genuinely overdue, and a healthy paid majority.
        plan = [
            ('paid', 0), ('paid', 0), ('paid', 0), ('paid', 0), ('paid', 0),
            ('partial', 55), ('partial', 40), ('partial', 70),
            ('unpaid', 0), ('unpaid', 0), ('unpaid', 0), ('unpaid', 0),
            ('draft', 0), ('draft', 0),
        ]
        overdue_at = {8, 9, 5}  # indexes whose due date lands in the past
        accepted = [q for q in quotations if q.status == 'accepted']
        made = 0

        for i, (status, paid_pct) in enumerate(plan):
            customer = customers[i % len(customers)]
            age = self.rng.randint(10, 100)
            due_offset = -self.rng.randint(3, 40) if i in overdue_at else self.rng.randint(4, 40)

            invoice = Invoice.objects.create(
                company=self.company, customer=customer, series=series,
                quotation=accepted[i] if i < len(accepted) else None,
                due_date=self.today + timedelta(days=due_offset),
                gst_percent=Decimal('18.00'), status=status,
            )
            for product in self.rng.sample(products, self.rng.randint(1, 3)):
                InvoiceItem.objects.create(
                    invoice=invoice, product=product,
                    quantity=self.rng.randint(1, 5),
                    unit_price=product.base_price,
                )

            total = invoice.get_grand_total()
            if status == 'paid':
                Payment.objects.create(
                    invoice=invoice, amount=total, payment_date=self.today - timedelta(days=self.rng.randint(1, 20)),
                    payment_method='neft', transaction_id=f'DEMO{100000 + i}',
                )
            elif status == 'partial':
                Payment.objects.create(
                    invoice=invoice, amount=(total * Decimal(paid_pct) / Decimal(100)).quantize(Decimal('0.01')),
                    payment_date=self.today - timedelta(days=self.rng.randint(1, 15)),
                    payment_method='neft', transaction_id=f'DEMO{200000 + i}',
                )

            self._backdate(Invoice, invoice.pk, 'date', age, is_date=True)
            made += 1
        self._log('invoices', made)

    def _equipment(self, customers, products):
        equipment = []
        for i in range(12):
            customer = customers[i % len(customers)]
            product = self.rng.choice(products)
            installed = self.today - timedelta(days=self.rng.randint(120, 1500))
            equipment.append(Equipment.objects.create(
                company=self.company, customer=customer, product=product,
                serial_number=f'SN-{2024000 + i * 137}',
                model_number=product.sku,
                model_description=product.name,
                installation_date=installed,
                installation_site=f'{customer.business_name} - Floor {1 + i % 4}',
                warranty_start_date=installed,
                warranty_end_date=installed + timedelta(days=365),
                notes=DEMO_TAG,
            ))
        self._log('equipment', len(equipment))
        return equipment

    def _amc_contracts(self, customers, products):
        made = 0
        for i in range(9):
            customer = customers[i % len(customers)]
            # Three of these land inside the 30-day renewal window so the
            # dashboard's "AMC expiring" tile is not permanently zero.
            if i < 3:
                end = self.today + timedelta(days=self.rng.randint(5, 28))
            elif i < 7:
                end = self.today + timedelta(days=self.rng.randint(60, 320))
            else:
                end = self.today - timedelta(days=self.rng.randint(10, 90))

            AMCContract.objects.create(
                company=self.company, customer=customer,
                product=self.rng.choice(products),
                serial_number=f'AMC-SN-{5000 + i}',
                start_date=end - timedelta(days=365),
                end_date=end,
                status='active' if end >= self.today else 'expired',
                pm_visits_per_year=self.rng.choice([2, 3, 4]),
            )
            made += 1
        self._log('AMC contracts', made)

    def _tickets(self, customers, equipment, engineers):
        # Enough open and urgent work that the service tiles and the workload
        # chart have something to show, with a realistic resolved majority.
        plan = (
            [('open', 'urgent')] * 2 + [('open', 'high')] * 2 + [('open', 'medium')] * 2 +
            [('assigned', 'high')] * 2 + [('in_progress', 'medium')] * 3 +
            [('in_progress', 'urgent')] * 1 + [('resolved', 'medium')] * 5 +
            [('closed', 'low')] * 4
        )
        made = 0
        for i, (status, priority) in enumerate(plan):
            customer = customers[i % len(customers)]
            title, description = PROBLEMS[i % len(PROBLEMS)]
            ticket = ServiceTicket.objects.create(
                company=self.company, customer=customer,
                equipment=equipment[i % len(equipment)],
                issue_title=title, description=description,
                priority=priority, status=status,
                outcome='pending' if status in ('open', 'assigned') and i % 3 == 0 else (
                    'completed' if status in ('resolved', 'closed') else ''
                ),
                reported_by_name=customer.user.get_full_name(),
                reported_by_mobile=f'98{self.rng.randint(10000000, 99999999)}',
            )
            # Leave the first few unassigned on purpose - "urgent / unassigned"
            # is one of the numbers the dashboard is meant to surface.
            if i >= 3:
                ticket.assigned_engineers.set(self.rng.sample(engineers, self.rng.randint(1, 2)))
            self._backdate(ServiceTicket, ticket.pk, 'created_at', self.rng.randint(1, 60))
            made += 1
        self._log('service tickets', made)

    def _staff_pm_tickets(self, engineers):
        """Assign and progress the PM tickets AMCContract.save() creates for us.

        Each AMC contract auto-generates one open, unassigned ticket per planned
        visit. Left alone that buries the real service workload under dozens of
        unassigned tickets, which is not what a running service desk looks like -
        so hand them to engineers and complete the visits that have already come
        round.
        """
        pm_ids = list(
            ServiceTicket.objects.filter(ticket_type='pm').values_list('pk', flat=True)
        )
        if not pm_ids:
            return

        self.rng.shuffle(pm_ids)
        done = len(pm_ids) * 2 // 3
        closed, resolved, still_open = pm_ids[:done // 2], pm_ids[done // 2:done], pm_ids[done:]

        ServiceTicket.objects.filter(pk__in=closed).update(status='closed', outcome='completed')
        ServiceTicket.objects.filter(pk__in=resolved).update(status='resolved', outcome='completed')

        through = ServiceTicket.assigned_engineers.through
        through.objects.bulk_create([
            through(serviceticket_id=pk, employee_id=self.rng.choice(engineers).pk)
            for pk in pm_ids
        ], ignore_conflicts=True)

        self._log('PM tickets staffed', len(pm_ids))
        self._log('  of which still open', len(still_open))

    def _stock(self):
        main = Godown.objects.create(
            company=self.company, name='Main Warehouse', godown_type='main',
            location=f'Ahmedabad {DEMO_TAG}',
        )
        van = Godown.objects.create(
            company=self.company, name='Service Van Stock', godown_type='sub',
            parent_godown=main, location=f'Mobile {DEMO_TAG}',
        )

        categories = {}
        items = []
        for cat_name, name, code, unit, reorder in STOCK_SEED:
            if cat_name not in categories:
                categories[cat_name] = StockCategory.objects.create(
                    company=self.company, name=f'{cat_name}',
                )
            items.append(StockItem.objects.create(
                company=self.company, category=categories[cat_name],
                name=name, item_code=code, unit=unit,
                reorder_level=Decimal(reorder), notes=DEMO_TAG,
            ))

        # Receive everything, then issue varying amounts so roughly a third of
        # the catalogue ends up at or below its reorder level.
        #
        # StockTransaction.clean() refuses to issue more than is in hand, but
        # objects.create() doesn't run clean(), so the split below has to keep its
        # own running balance - otherwise the demo ships negative stock.
        transactions = 0
        for i, item in enumerate(items):
            reorder = float(item.reorder_level)
            received = round(reorder * self.rng.uniform(2.0, 4.0), 2)
            StockTransaction.objects.create(
                company=self.company, stock_item=item, godown=main,
                transaction_type='receipt', quantity=Decimal(str(received)),
                transaction_date=self.today - timedelta(days=self.rng.randint(30, 120)),
                remarks=f'Opening purchase {DEMO_TAG}',
            )
            transactions += 1

            # Every third item is driven to or below its reorder level.
            target_ratio = self.rng.uniform(0.25, 0.85) if i % 3 == 0 else self.rng.uniform(1.2, 2.6)
            remaining = max(received - reorder * target_ratio, 0)
            splits = self.rng.randint(1, 3)
            for n in range(splits):
                if remaining <= 0:
                    break
                # Last split takes whatever is left, so the parts sum to the total.
                chunk = round(remaining if n == splits - 1 else remaining / (splits - n), 2)
                chunk = min(chunk, remaining)
                if chunk <= 0:
                    continue
                StockTransaction.objects.create(
                    company=self.company, stock_item=item,
                    godown=self.rng.choice([main, van]),
                    transaction_type='issue', quantity=Decimal(str(chunk)),
                    transaction_date=self.today - timedelta(days=self.rng.randint(1, 28)),
                    party_type='employee',
                    remarks=f'Site consumption {DEMO_TAG}',
                )
                remaining = round(remaining - chunk, 2)
                transactions += 1

        self._log('stock items', len(items))
        self._log('stock transactions', transactions)
        return items, [main, van]

    def _projects(self, customers):
        statuses = ['planning', 'procurement', 'in_progress', 'in_progress', 'on_hold', 'completed']
        projects = []
        for i, name in enumerate(PROJECT_NAMES):
            projects.append(Project.objects.create(
                company=self.company, customer=customers[i % len(customers)],
                name=name, status=statuses[i],
                start_date=self.today - timedelta(days=self.rng.randint(10, 150)),
                expected_completion_date=self.today + timedelta(days=self.rng.randint(10, 120)),
                notes=DEMO_TAG,
            ))
        self._log('projects', len(projects))
        return projects

    def _requisitions(self, projects, stock_items):
        made_pr = made_items = 0
        for i, project in enumerate(projects[:5]):
            pr = PurchaseRequisition.objects.create(
                company=self.company, project=project,
                remarks=f'Material for {project.name} {DEMO_TAG}',
            )
            made_pr += 1
            for item in self.rng.sample(stock_items, self.rng.randint(2, 5)):
                PurchaseRequisitionItem.objects.create(
                    purchase_requisition=pr, stock_item=item,
                    quantity=Decimal(self.rng.randint(2, 25)),
                    status=self.rng.choice(['pending', 'pending', 'ordered', 'issued', 'received']),
                )
                made_items += 1
        self._log('purchase requisitions', made_pr)
        self._log('requisition items', made_items)

    def _suppliers_and_pos(self, projects):
        suppliers = [
            Supplier.objects.create(
                company=self.company, name=name,
                contact_person=self.rng.choice(CONTACTS),
                phone=f'99{self.rng.randint(10000000, 99999999)}',
                email=f'sales@{name.split()[0].lower()}.example.com',
                payment_terms='30 days from invoice date',
                notes=DEMO_TAG,
            )
            for name in SUPPLIERS
        ]
        statuses = ['draft', 'sent', 'sent', 'confirmed', 'confirmed',
                    'received', 'received', 'received', 'received', 'cancelled']
        for i, status in enumerate(statuses):
            SupplierPurchaseOrder.objects.create(
                company=self.company, supplier=suppliers[i % len(suppliers)],
                project=projects[i % len(projects)], status=status,
                order_date=self.today - timedelta(days=self.rng.randint(5, 90)),
                expected_delivery_date=self.today + timedelta(days=self.rng.randint(-10, 30)),
                remarks=DEMO_TAG,
            )
        self._log('suppliers', len(suppliers))
        self._log('supplier POs', len(statuses))

    def _backdate(self, model, pk, field, days_ago, is_date=False):
        """Push an auto_now_add timestamp into the past.

        auto_now_add ignores whatever you pass to create(), so the value has to be
        rewritten with an UPDATE that bypasses save().
        """
        value = self.today - timedelta(days=days_ago)
        if not is_date:
            value = timezone.make_aware(
                timezone.datetime.combine(value, timezone.datetime.min.time())
            )
        model.objects.filter(pk=pk).update(**{field: value})
