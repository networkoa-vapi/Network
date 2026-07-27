import csv
import os
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from core.models import Company, Division, ProductCategory, ProductSubCategory, Product


class Command(BaseCommand):
    help = (
        'Import products from a CSV file into the database.\n'
        'Expected CSV columns:\n'
        '  S.No, Division, Category, Subcategory, Model / SKU, Model Number,\n'
        '  Product Name, Capacity / Specs, Series, Model Year, Price MOP (INR),\n'
        '  MRP (INR), Availability, Product Page URL, Brochure / Catalogue PDF'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the product master CSV file'
        )
        parser.add_argument(
            '--company-name',
            type=str,
            default='Network Office Automation',
            help='Company name to associate products with (default: Network Office Automation)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and validate the CSV without writing to the database'
        )
        parser.add_argument(
            '--price-field',
            type=str,
            default='mop',
            choices=['mop', 'mrp'],
            help='Which price column to use as base_price: "mop" (Market Operating Price) or "mrp" (default: mop)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        company_name = options['company_name']
        dry_run = options['dry_run']
        price_field = options['price_field']

        # ── Validate file ──────────────────────────────────────
        if not os.path.isfile(csv_path):
            raise CommandError(f'File not found: {csv_path}')

        # ── Get or create company ──────────────────────────────
        try:
            company = Company.objects.get(name=company_name)
            self.stdout.write(f'Using existing company: {company}')
        except Company.DoesNotExist:
            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f'Company "{company_name}" not found (dry-run mode, skipping creation)'
                ))
                company = None
            else:
                raise CommandError(
                    f'Company "{company_name}" not found. '
                    f'Create it first or use --company-name to specify an existing company.'
                )

        # ── Purge existing products ────────────────────────────
        if not dry_run and company:
            deleted_count, _ = Product.objects.filter(company=company).delete()
            self.stdout.write(self.style.WARNING(f'Purged {deleted_count} existing products. The CSV will now be the sole source of truth.'))

        # ── Caches for divisions, categories & subcategories ───
        division_cache = {}       # "Division Name" -> Division instance
        category_cache = {}       # "Category Name" -> ProductCategory instance
        subcategory_cache = {}    # ("Category Name", "Subcategory Name") -> ProductSubCategory instance

        # ── Counters ───────────────────────────────────────────
        created = 0
        updated = 0
        skipped = 0
        errors = []

        # ── Read CSV ───────────────────────────────────────────
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # Validate headers
            required_headers = {'Category', 'Subcategory', 'Model / SKU', 'Product Name'}
            actual_headers = set(reader.fieldnames or [])
            missing = required_headers - actual_headers
            if missing:
                raise CommandError(
                    f'CSV is missing required columns: {", ".join(sorted(missing))}\n'
                    f'Found columns: {", ".join(reader.fieldnames or [])}'
                )

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    sku = (row.get('Model / SKU') or '').strip()
                    if not sku:
                        skipped += 1
                        continue

                    product_name = (row.get('Product Name') or '').strip()
                    if not product_name:
                        product_name = sku  # fallback to SKU as name

                    model_number = (row.get('Model Number') or '').strip() or None
                    category_name = (row.get('Category') or '').strip()
                    subcategory_name = (row.get('Subcategory') or '').strip()

                    # ── Direct field mappings ──────────────────
                    capacity = (row.get('Capacity / Specs') or '').strip()
                    series = (row.get('Series') or '').strip()
                    model_year = (row.get('Model Year') or '').strip()
                    division_raw = (row.get('Division') or '').strip().lower()
                    
                    division_name = None
                    if 'consumer' in division_raw:
                        division_name = 'Consumer'
                    elif 'commercial' in division_raw:
                        division_name = 'Commercial'

                    division = None
                    if division_name and not dry_run:
                        if division_name not in division_cache:
                            div_obj, _ = Division.objects.get_or_create(
                                company=company,
                                name=division_name
                            )
                            division_cache[division_name] = div_obj
                        division = division_cache[division_name]

                    product_url = (row.get('Product Page URL') or '').strip() or None
                    brochure_url = (row.get('Brochure / Catalogue PDF') or '').strip() or None

                    # ── Parse price ────────────────────────────
                    def parse_price(val):
                        if not val:
                            return None
                        val = val.replace(',', '').strip()
                        if not val:
                            return None
                        try:
                            return Decimal(val)
                        except InvalidOperation:
                            return None

                    mop_price = parse_price(row.get('Price MOP (INR)'))
                    mrp_price = parse_price(row.get('MRP (INR)'))

                    base_price = Decimal('0.00')
                    if price_field == 'mrp' and mrp_price is not None:
                        base_price = mrp_price
                    elif mop_price is not None:
                        base_price = mop_price
                    elif mrp_price is not None: # Fallback if MOP is empty
                        base_price = mrp_price

                    if mop_price is None and mrp_price is None:
                         base_price = Decimal('0.00')

                    # ── Availability ───────────────────────────
                    availability_raw = (row.get('Availability') or '').strip().lower()
                    if availability_raw in ('in stock', 'available', 'yes', 'true', '1'):
                        availability_status = 'in_stock'
                        is_active = True
                    elif availability_raw in ('out of stock', 'no', 'false', '0'):
                        availability_status = 'out_of_stock'
                        is_active = True
                    elif availability_raw in ('discontinued',):
                        availability_status = 'discontinued'
                        is_active = False
                    else:
                        availability_status = 'in_stock'
                        is_active = True

                    if dry_run:
                        self.stdout.write(
                            f'  [DRY-RUN] Row {row_num}: SKU={sku}, '
                            f'Category={category_name}, SubCat={subcategory_name}, '
                            f'Price={base_price}, Active={is_active}'
                        )
                        created += 1
                        continue

                    # ── Get or Create Category ─────────────────
                    if category_name:
                        if category_name not in category_cache:
                            cat_obj, _ = ProductCategory.objects.get_or_create(
                                company=company,
                                name=category_name,
                                defaults={
                                    'description': f'Auto-imported: {category_name}',
                                    'division': division
                                }
                            )
                            # Ensure division is set if it was missing previously
                            if cat_obj.division != division and not dry_run:
                                cat_obj.division = division
                                cat_obj.save()
                            category_cache[category_name] = cat_obj
                        category = category_cache[category_name]
                    else:
                        category = None

                    # ── Get or Create Subcategory ──────────────
                    subcategory = None
                    if subcategory_name and category:
                        cache_key = (category_name, subcategory_name)
                        if cache_key not in subcategory_cache:
                            subcat_obj, _ = ProductSubCategory.objects.get_or_create(
                                company=company,
                                category=category,
                                name=subcategory_name,
                                defaults={'description': f'Auto-imported: {subcategory_name}'}
                            )
                            subcategory_cache[cache_key] = subcat_obj
                        subcategory = subcategory_cache[cache_key]

                    # ── Create or Update Product ───────────────
                    product, was_created = Product.objects.update_or_create(
                        sku=sku,
                        defaults={
                            'company': company,
                            'category': category,
                            'subcategory': subcategory,
                            'name': product_name,
                            'model_number': model_number,
                            'division': division,
                            'series': series,
                            'model_year': model_year,
                            'specifications': capacity,
                            'base_price': base_price,
                            'mrp': mrp_price,
                            'availability_status': availability_status,
                            'is_active': is_active,
                            'product_url': product_url,
                            'brochure_url': brochure_url,
                        }
                    )

                    if was_created:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
                    skipped += 1

        # ── Summary ────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write('=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING('  DRY-RUN COMPLETE (no changes written)'))
        else:
            self.stdout.write(self.style.SUCCESS('  IMPORT COMPLETE'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'  Created  : {created} products')
        self.stdout.write(f'  Updated  : {updated} products')
        self.stdout.write(f'  Skipped  : {skipped} rows')
        self.stdout.write(f'  Categories created : {len(category_cache)}')
        self.stdout.write(f'  Subcategories created : {len(subcategory_cache)}')
        self.stdout.write('=' * 60)

        if errors:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(f'  {len(errors)} error(s):'))
            for err in errors:
                self.stdout.write(self.style.ERROR(f'    • {err}'))
