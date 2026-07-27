from django.core.management.base import BaseCommand
from core.models import Company, ProductCategory, Product

class Command(BaseCommand):
    help = 'Seeds the database with a massive catalog of Blue Star India products'

    def handle(self, *args, **kwargs):
        # Ensure company exists
        company, _ = Company.objects.get_or_create(
            name='Network Office Automation', 
            brand_name='NOA', 
            contact_email='info@noa.com', 
            contact_phone='9999999999'
        )

        categories = {
            'RAC': 'Room Air Conditioners (Split & Window)',
            'CAC': 'Commercial Air Conditioning (Cassette, Ducted)',
            'CREF': 'Commercial Refrigeration (Freezers, Coolers)',
            'WATER': 'Water Purifiers & Dispensers',
            'AIR': 'Air Purifiers'
        }
        
        db_categories = {}
        for code, name in categories.items():
            cat, _ = ProductCategory.objects.get_or_create(company=company, name=name)
            db_categories[code] = cat

        # Define products dataset
        # Format: (CategoryCode, SKU, Name, Specs, Terms, Price)
        products = [
            # ROOM ACs
            ('RAC', 'IC312YNU', 'Blue Star 1 Ton 3 Star Inverter Split AC', '1 Ton, Inverter Compressor, Copper Condenser, R32 Refrigerant', '1 Yr Comprehensive, 5 Yrs PCB, 10 Yrs Compressor. Installation Extra.', 32990.00),
            ('RAC', 'IC318YNU', 'Blue Star 1.5 Ton 3 Star Inverter Split AC', '1.5 Ton, Inverter Compressor, Copper Condenser, R32 Refrigerant', '1 Yr Comprehensive, 5 Yrs PCB, 10 Yrs Compressor. Installation Extra.', 36990.00),
            ('RAC', 'IC518YNU', 'Blue Star 1.5 Ton 5 Star Inverter Split AC', '1.5 Ton, 5 Star, Inverter Compressor, Copper Condenser, R32', '1 Yr Comprehensive, 5 Yrs PCB, 10 Yrs Compressor. Installation Extra.', 42990.00),
            ('RAC', 'IC324YNU', 'Blue Star 2.0 Ton 3 Star Inverter Split AC', '2 Ton, 3 Star, Inverter Compressor, Copper Condenser, R32', '1 Yr Comprehensive, 5 Yrs PCB, 10 Yrs Compressor. Installation Extra.', 52990.00),
            ('RAC', 'IC524YNU', 'Blue Star 2.0 Ton 5 Star Inverter Split AC', '2 Ton, 5 Star, Inverter Compressor, Copper Condenser, R32', '1 Yr Comprehensive, 5 Yrs PCB, 10 Yrs Compressor. Installation Extra.', 58990.00),
            ('RAC', 'FS312YNU', 'Blue Star 1 Ton 3 Star Fixed Speed Split AC', '1 Ton, Fixed Speed, Copper Condenser, R32', '1 Yr Comprehensive, 5 Yrs Compressor. Installation Extra.', 29990.00),
            ('RAC', 'FS318YNU', 'Blue Star 1.5 Ton 3 Star Fixed Speed Split AC', '1.5 Ton, Fixed Speed, Copper Condenser, R32', '1 Yr Comprehensive, 5 Yrs Compressor. Installation Extra.', 33990.00),
            ('RAC', 'WAC315YNU', 'Blue Star 1.5 Ton 3 Star Window AC', '1.5 Ton, Window AC, Copper Condenser', '1 Yr Comprehensive, 5 Yrs Compressor. Installation Extra.', 28990.00),
            ('RAC', 'WAC515YNU', 'Blue Star 1.5 Ton 5 Star Window AC', '1.5 Ton, 5 Star, Window AC, Copper Condenser', '1 Yr Comprehensive, 5 Yrs Compressor. Installation Extra.', 33990.00),
            ('RAC', 'PAC101', 'Blue Star 1 Ton Portable AC', '1 Ton, Portable, Castor Wheels, R410A', '1 Yr Comprehensive, 1 Yr Compressor.', 26990.00),
            
            # COMMERCIAL ACs
            ('CAC', 'CAS-20TR', 'Blue Star 2.0 Ton Cassette AC', '2 Ton, Cassette AC, Scroll Compressor, R410A', '1 Yr Comprehensive, 1 Yr Compressor. Installation Extra.', 65000.00),
            ('CAC', 'CAS-30TR', 'Blue Star 3.0 Ton Cassette AC', '3 Ton, Cassette AC, Scroll Compressor, R410A', '1 Yr Comprehensive, 1 Yr Compressor. Installation Extra.', 85000.00),
            ('CAC', 'CAS-40TR', 'Blue Star 4.0 Ton Cassette AC', '4 Ton, Cassette AC, Scroll Compressor, R410A', '1 Yr Comprehensive, 1 Yr Compressor. Installation Extra.', 105000.00),
            ('CAC', 'DUC-55TR', 'Blue Star 5.5 Ton Ducted Split AC', '5.5 Ton, Ducted Split, Twin Rotary Compressor, R410A', '1 Yr Comprehensive, 1 Yr Compressor. Installation & Ducting Extra.', 125000.00),
            ('CAC', 'DUC-85TR', 'Blue Star 8.5 Ton Ducted Split AC', '8.5 Ton, Ducted Split, Scroll Compressor, R410A', '1 Yr Comprehensive, 1 Yr Compressor. Installation & Ducting Extra.', 180000.00),
            ('CAC', 'DUC-110TR', 'Blue Star 11.0 Ton Ducted Split AC', '11 Ton, Ducted Split, Scroll Compressor, R410A', '1 Yr Comprehensive, 1 Yr Compressor. Installation & Ducting Extra.', 220000.00),
            ('CAC', 'VER-30TR', 'Blue Star 3.0 Ton Verticool Tower AC', '3 Ton, Tower/Floor Standing AC, R410A', '1 Yr Comprehensive, 1 Yr Compressor.', 82000.00),
            ('CAC', 'VER-40TR', 'Blue Star 4.0 Ton Verticool Tower AC', '4 Ton, Tower/Floor Standing AC, R410A', '1 Yr Comprehensive, 1 Yr Compressor.', 105000.00),
            
            # COMMERCIAL REFRIGERATION
            ('CREF', 'CHF-100', 'Blue Star 100 Ltr Hard Top Deep Freezer', '100 Liters, Hard Top, Single Door, Manual Defrost', '1 Yr Comprehensive, 3 Yrs Compressor.', 13500.00),
            ('CREF', 'CHF-200', 'Blue Star 200 Ltr Hard Top Deep Freezer', '200 Liters, Hard Top, Single Door, Manual Defrost', '1 Yr Comprehensive, 3 Yrs Compressor.', 17500.00),
            ('CREF', 'CHF-300', 'Blue Star 300 Ltr Hard Top Deep Freezer', '300 Liters, Hard Top, Double Door, Manual Defrost', '1 Yr Comprehensive, 3 Yrs Compressor.', 21500.00),
            ('CREF', 'CHF-400', 'Blue Star 400 Ltr Hard Top Deep Freezer', '400 Liters, Hard Top, Double Door, Manual Defrost', '1 Yr Comprehensive, 3 Yrs Compressor.', 24500.00),
            ('CREF', 'CHF-500', 'Blue Star 500 Ltr Hard Top Deep Freezer', '500 Liters, Hard Top, Double Door, Manual Defrost', '1 Yr Comprehensive, 3 Yrs Compressor.', 27500.00),
            ('CREF', 'CGF-300', 'Blue Star 300 Ltr Glass Top Deep Freezer', '300 Liters, Glass Top, Sliding Door', '1 Yr Comprehensive, 1 Yr Compressor.', 25000.00),
            ('CREF', 'CGF-400', 'Blue Star 400 Ltr Glass Top Deep Freezer', '400 Liters, Glass Top, Sliding Door', '1 Yr Comprehensive, 1 Yr Compressor.', 29000.00),
            ('CREF', 'SCL-40', 'Blue Star 40 Ltr Water Cooler (SDLX4080)', '40 Liters Storage, 40 Liters Cooling Capacity, Full Stainless Steel', '1 Yr Comprehensive.', 32000.00),
            ('CREF', 'SCL-80', 'Blue Star 80 Ltr Water Cooler (SDLX80120)', '80 Liters Storage, 80 Liters Cooling Capacity, Full Stainless Steel', '1 Yr Comprehensive.', 45000.00),
            ('CREF', 'SCL-150', 'Blue Star 150 Ltr Water Cooler (SDLX150150)', '150 Liters Storage, 150 Liters Cooling Capacity, Full Stainless Steel', '1 Yr Comprehensive.', 58000.00),
            ('CREF', 'BWC-3', 'Blue Star Bottom Loading Water Dispenser', 'Bottom Loading, Hot/Cold/Normal, 3 Taps', '1 Yr Comprehensive.', 8500.00),
            ('CREF', 'TWC-3', 'Blue Star Top Loading Water Dispenser (With Refrigerator)', 'Top Loading, Hot/Cold/Normal, 14 Ltr Refrigerator Cabinet', '1 Yr Comprehensive.', 9500.00),
            ('CREF', 'VC-300', 'Blue Star 300 Ltr Visi Cooler', '300 Liters, Vertical Glass Door Cooler, LED Lighting', '1 Yr Comprehensive.', 31000.00),
            ('CREF', 'VC-400', 'Blue Star 400 Ltr Visi Cooler', '400 Liters, Vertical Glass Door Cooler, LED Lighting', '1 Yr Comprehensive.', 38000.00),
            
            # WATER PURIFIERS & APPLIANCES
            ('WATER', 'WP-EXC1', 'Blue Star Excella Water Purifier', 'RO + UV + UF, 6 Ltr Storage, Black', '1 Yr Comprehensive.', 9500.00),
            ('WATER', 'WP-ELE1', 'Blue Star Eleanor Water Purifier', 'RO + UV + UF + Alkaline, 8 Ltr Storage, Aqua Gold', '1 Yr Comprehensive.', 14500.00),
            ('WATER', 'WP-OPE1', 'Blue Star Opulus Water Purifier', 'RO + UV, 8 Ltr Storage, White', '1 Yr Comprehensive.', 12500.00),
            ('AIR', 'AP-BS300', 'Blue Star Air Purifier (300 Sq Ft)', 'HEPA Filter, Activated Carbon, Covers 300 Sq Ft', '1 Yr Comprehensive.', 8990.00),
            ('AIR', 'AP-BS500', 'Blue Star Air Purifier (500 Sq Ft)', 'HEPA Filter, Activated Carbon, Covers 500 Sq Ft, Auto Mode', '1 Yr Comprehensive.', 12990.00),
        ]

        created_count = 0
        updated_count = 0
        
        for cat_code, sku, name, specs, terms, price in products:
            product, created = Product.objects.update_or_create(
                sku=sku,
                company=company,
                defaults={
                    'category': db_categories[cat_code],
                    'name': name,
                    'specifications': specs,
                    'product_specific_terms': terms,
                    'base_price': price,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded Blue Star catalog! Created: {created_count}, Updated: {updated_count} products.'))
