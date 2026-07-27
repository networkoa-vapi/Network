from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from datetime import timedelta
from smart_selects.db_fields import ChainedForeignKey
from datetime import timedelta


# ─────────────────────────────────────────────────────────────
# Indian State Choices (with GST State Codes)
# ─────────────────────────────────────────────────────────────
INDIAN_STATE_CHOICES = (
    ('01', '01 - Jammu & Kashmir'),
    ('02', '02 - Himachal Pradesh'),
    ('03', '03 - Punjab'),
    ('04', '04 - Chandigarh'),
    ('05', '05 - Uttarakhand'),
    ('06', '06 - Haryana'),
    ('07', '07 - Delhi'),
    ('08', '08 - Rajasthan'),
    ('09', '09 - Uttar Pradesh'),
    ('10', '10 - Bihar'),
    ('11', '11 - Sikkim'),
    ('12', '12 - Arunachal Pradesh'),
    ('13', '13 - Nagaland'),
    ('14', '14 - Manipur'),
    ('15', '15 - Mizoram'),
    ('16', '16 - Tripura'),
    ('17', '17 - Meghalaya'),
    ('18', '18 - Assam'),
    ('19', '19 - West Bengal'),
    ('20', '20 - Jharkhand'),
    ('21', '21 - Odisha'),
    ('22', '22 - Chhattisgarh'),
    ('23', '23 - Madhya Pradesh'),
    ('24', '24 - Gujarat'),
    ('25', '25 - Daman & Diu'),
    ('26', '26 - Dadra & Nagar Haveli'),
    ('27', '27 - Maharashtra'),
    ('28', '28 - Andhra Pradesh (Old)'),
    ('29', '29 - Karnataka'),
    ('30', '30 - Goa'),
    ('31', '31 - Lakshadweep'),
    ('32', '32 - Kerala'),
    ('33', '33 - Tamil Nadu'),
    ('34', '34 - Puducherry'),
    ('35', '35 - Andaman & Nicobar Islands'),
    ('36', '36 - Telangana'),
    ('37', '37 - Andhra Pradesh (New)'),
    ('38', '38 - Ladakh'),
)

INDUSTRY_TYPE_CHOICES = (
    ('hvac', 'HVAC & Air Conditioning'),
    ('refrigeration', 'Refrigeration'),
    ('electrical', 'Electrical'),
    ('plumbing', 'Plumbing'),
    ('fire_safety', 'Fire Safety'),
    ('elevator', 'Elevator & Escalator'),
    ('solar', 'Solar & Renewable Energy'),
    ('it_services', 'IT Services'),
    ('manufacturing', 'Manufacturing'),
    ('construction', 'Construction'),
    ('other', 'Other'),
)

BUSINESS_TYPE_CHOICES = (
    ('proprietorship', 'Proprietorship'),
    ('partnership', 'Partnership'),
    ('llp', 'Limited Liability Partnership'),
    ('pvt_ltd', 'Private Limited'),
    ('public_ltd', 'Public Limited'),
    ('opc', 'One Person Company'),
    ('trust', 'Trust / Society'),
    ('other', 'Other'),
)


class Company(models.Model):
    """
    The foundational Tenant model for NOA ERP.
    Captures all Indian statutory and business details required for compliance.
    """

    # ── Business Identity ──────────────────────────────────
    name = models.CharField(
        max_length=255,
        help_text="Legal registered name of the business"
    )
    brand_name = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Trading name or brand name (if different from legal name)"
    )
    logo = models.ImageField(
        upload_to='company_logos/', blank=True, null=True,
        help_text="Company logo (recommended: 200×200 px)"
    )
    business_type = models.CharField(
        max_length=20, choices=BUSINESS_TYPE_CHOICES,
        default='proprietorship',
        help_text="Legal structure of the business"
    )
    industry_type = models.CharField(
        max_length=20, choices=INDUSTRY_TYPE_CHOICES,
        default='hvac',
        help_text="Primary industry / service domain"
    )
    website = models.URLField(blank=True, null=True)

    # ── Indian Statutory Details ───────────────────────────
    gstin = models.CharField(
        max_length=15, blank=True, null=True,
        verbose_name="GSTIN",
        help_text="15-digit GST Identification Number (e.g., 27AABCU9603R1ZM)"
    )
    pan = models.CharField(
        max_length=10, blank=True, null=True,
        verbose_name="PAN",
        help_text="10-character Permanent Account Number (e.g., AABCU9603R)"
    )
    cin = models.CharField(
        max_length=21, blank=True, null=True,
        verbose_name="CIN",
        help_text="21-character Corporate Identification Number"
    )
    tan = models.CharField(
        max_length=10, blank=True, null=True,
        verbose_name="TAN",
        help_text="Tax Deduction and Collection Account Number"
    )
    msme_number = models.CharField(
        max_length=20, blank=True, null=True,
        verbose_name="MSME / Udyam Number",
        help_text="Udyam Registration Number (e.g., UDYAM-XX-00-0000000)"
    )
    gst_state_code = models.CharField(
        max_length=2, choices=INDIAN_STATE_CHOICES,
        blank=True, null=True,
        verbose_name="GST State Code",
        help_text="State code as per GST registration"
    )

    # ── Registered Address ─────────────────────────────────
    address_line_1 = models.CharField(
        max_length=255,
        help_text="Building / Floor / Street"
    )
    address_line_2 = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Area / Landmark"
    )
    city = models.CharField(max_length=100)
    state = models.CharField(
        max_length=2, choices=INDIAN_STATE_CHOICES,
        help_text="State / Union Territory"
    )
    pincode = models.CharField(
        max_length=6,
        help_text="6-digit PIN code"
    )

    # ── Contact Details ────────────────────────────────────
    contact_email = models.EmailField(
        help_text="Primary business email"
    )
    contact_phone = models.CharField(
        max_length=15,
        help_text="Primary phone with country code (e.g., +919876543210)"
    )
    alternate_phone = models.CharField(
        max_length=15, blank=True, null=True,
        help_text="Secondary / landline number"
    )

    # ── Bank Details (for invoicing) ───────────────────────
    bank_name = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Name of the bank"
    )
    bank_account_number = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Bank account number"
    )
    bank_ifsc = models.CharField(
        max_length=11, blank=True, null=True,
        verbose_name="IFSC Code",
        help_text="11-character IFSC code (e.g., SBIN0001234)"
    )
    bank_branch = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Branch name"
    )

    # ── Platform Management ────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        help_text="Disable to suspend this company's access"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.brand_name or self.name


def get_default_company():
    """NOA ERP now serves a single tenant (NOA) — pre-select it everywhere by default."""
    return Company.objects.order_by('pk').values_list('pk', flat=True).first()


class User(AbstractUser):
    """Custom User model separating roles within NOA ERP"""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=get_default_company,
        related_name='users'
    )

    role = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='role_users', help_text="Dynamic Role Assignment")

    def __str__(self):
        return f"{self.username} ({self.role})"


class CustomerProfile(models.Model):
    """Industrial or residential clients linked to a specific company"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company, related_name='customers')
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role__name': 'Customer'})
    business_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    billing_address = models.TextField()
    shipping_address = models.TextField(help_text="Primary installation site")

    def __str__(self):
        return self.business_name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company, related_name='employees')
    employee_code = models.CharField(max_length=50, unique=True)
    
    # Professional Details
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1, help_text="Total years of experience")
    specific_expertise = models.TextField(blank=True, help_text="Specific skills or product expertise")
    education_qualification = models.CharField(max_length=255)
    
    # Personal & Contact Details
    contact_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True)
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HRMS - Employee Master"
        verbose_name_plural = "HRMS - Employee Master"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.designation}"


class Division(models.Model):
    """Business divisions like Consumer, Commercial"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Division"
        verbose_name_plural = "Divisions"
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    """Categories like Room AC, Water Cooler, Industrial Chillers"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


class ProductSubCategory(models.Model):
    """Sub-categories like Split AC, Window AC, Inverter AC"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Product Sub-Categories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Product(models.Model):
    """The actual assets and equipment sold"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)

    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    model_number = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Model Number",
        help_text="Manufacturer model number (e.g. CSTO-18ADYA)"
    )
    specifications = models.TextField(
        blank=True, null=True,
        help_text="Capacity / technical specs (e.g. 1.5 Ton 5 Star)"
    )
    series = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Product series (e.g. D SERIES, Q SMART WI-FI SERIES)"
    )
    model_year = models.CharField(
        max_length=10, blank=True, null=True,
        help_text="Model / BEE label year (e.g. 2025, 2026)"
    )
    product_specific_terms = models.TextField(
        blank=True, null=True,
        help_text="Terms specific to this product to appear on quotes."
    )

    # ── Pricing ────────────────────────────────────────────
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Market Operating Price (MOP) in INR"
    )
    mrp = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True,
        verbose_name="MRP",
        help_text="Maximum Retail Price in INR"
    )

    # ── Availability ───────────────────────────────────────
    AVAILABILITY_CHOICES = (
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    )
    availability_status = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES,
        default='in_stock',
        help_text="Current stock availability"
    )
    is_active = models.BooleanField(default=True)

    # ── Links ──────────────────────────────────────────────
    product_url = models.URLField(
        blank=True, null=True,
        verbose_name="Product Page URL",
        help_text="Official product page link"
    )
    brochure_url = models.URLField(
        blank=True, null=True,
        verbose_name="Brochure / Catalogue URL",
        help_text="PDF brochure or catalogue link"
    )

    def __str__(self):
        return f"{self.sku} - {self.name}"

class ProductDocument(models.Model):
    """PDF Library for Product Catalogues, Brochures, and Manuals"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, help_text="Link to a division")
    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documents', help_text="Link to an entire category (e.g. all RACs)"
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Link to a sub-category"
    )
    product = ChainedForeignKey(
        Product,
        chained_field="subcategory",
        chained_model_field="subcategory",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documents', help_text="Link to a specific product"
    )
    
    title = models.CharField(max_length=255, help_text="e.g. 'Blue Star 2024 AC Brochure'")
    
    DOC_TYPES = (
        ('brochure', 'Brochure / Catalogue'),
        ('manual', 'User Manual'),
        ('spec_sheet', 'Specification Sheet'),
        ('other', 'Other'),
    )
    document_type = models.CharField(max_length=20, choices=DOC_TYPES, default='brochure')
    
    file = models.FileField(upload_to='product_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────
# CRM & Sales Module
# ─────────────────────────────────────────────────────────────

class Inquiry(models.Model):
    """Pre-sales inquiry tracking"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    customer_profile = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, help_text="Link if existing customer")
    
    SOURCE_CHOICES = (
        ('email', 'Email'),
        ('phone', 'Phone/Telephone'),
        ('walkin', 'Walk-in'),
        ('website', 'Website'),
        ('other', 'Other'),
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='phone')
    
    name = models.CharField(max_length=255, help_text="Prospect Name")
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    requirement = models.TextField(help_text="Generic requirement description", blank=True, null=True)
    
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('quoted', 'Quotation Sent'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user__role__name__in': ['Admin', 'Sales']})
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"Inquiry: {self.name} - {self.get_status_display()}"


class InquiryItem(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='items')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    product = ChainedForeignKey(
        Product,
        chained_field="subcategory",
        chained_model_field="subcategory",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Unknown'}"


class Quotation(models.Model):
    """Standard Quotation generation with standard terms"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, null=True, blank=True)
    
    quotation_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Internal Discount provision (Only admin handles)
    admin_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Overall discount % applied by Admin")
    
    # Standard Terms & Conditions
    terms_and_conditions = models.TextField(default="1. Validity: 30 Days.\n2. Payment: 100% Advance.\n3. Delivery: 2-3 Weeks.", help_text="Standard terms applied to this quotation.")
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent to Customer'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    
    prepared_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.quotation_number:
            import uuid
            self.quotation_number = f"QT-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
        
    def get_subtotal(self):
        return sum(item.get_line_total() for item in self.items.all())
        
    def get_final_total(self):
        subtotal = self.get_subtotal()
        discount_amount = subtotal * (self.admin_discount_percent / 100)
        return subtotal - discount_amount

    def __str__(self):
        name = self.inquiry.name if self.inquiry else (self.customer.business_name if self.customer else "Unknown")
        return f"{self.quotation_number} - {name}"

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    product = ChainedForeignKey(
        Product,
        chained_field="subcategory",
        chained_model_field="subcategory",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, help_text="Auto-pulled from product base price if left blank")
    
    def save(self, *args, **kwargs):
        if not self.unit_price and self.product:
            self.unit_price = self.product.base_price
        super().save(*args, **kwargs)
        
    def get_line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class PurchaseOrder(models.Model):
    """Customer's Purchase Order issued against a Quotation; defines the agreed payment terms"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE, related_name='purchase_order', null=True, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)

    po_number = models.CharField(max_length=100, help_text="Customer's PO reference number")
    po_date = models.DateField(help_text="Date on the customer's PO")
    po_file = models.FileField(upload_to='purchase_orders/', blank=True, null=True, help_text="Scanned copy of the PO document")

    payment_terms = models.TextField(help_text="Payment terms as specified in the PO, e.g. '50% advance, 50% before dispatch'")
    po_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Total PO value (defaults to quotation total if left blank)")

    STATUS_CHOICES = (
        ('received', 'Received'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.po_amount and self.quotation:
            self.po_amount = self.quotation.get_final_total()

        is_new = self.pk is None
        previous_status = None
        if not is_new:
            previous_status = PurchaseOrder.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        super().save(*args, **kwargs)

        just_confirmed = self.status == 'confirmed' and previous_status != 'confirmed'
        if just_confirmed and not hasattr(self, 'sales_order'):
            series = SalesOrderSeries.objects.filter(company=self.company, is_active=True).order_by('-pk').first()
            sales_order = SalesOrder.objects.create(
                company=self.company,
                purchase_order=self,
                quotation=self.quotation,
                customer=self.customer,
                series=series,
            )
            if self.quotation:
                for item in self.quotation.items.all():
                    SalesOrderItem.objects.create(
                        sales_order=sales_order,
                        division=item.division,
                        category=item.category,
                        subcategory=item.subcategory,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                    )

    def __str__(self):
        return f"PO {self.po_number} - {self.customer.business_name}"


class SalesOrderSeries(models.Model):
    """Custom Prefix for Auto-generating year-wise Sales Order numbers (e.g. one series per financial year)"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    name = models.CharField(max_length=50, help_text="e.g. FY 26-27 Sales Orders")
    prefix = models.CharField(max_length=20, help_text="e.g. SO/26-27/")
    next_number = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True, help_text="Auto-generated Sales Orders use the active series for the company. Keep only one active per company/year.")

    class Meta:
        verbose_name = "Sales Order Series"
        verbose_name_plural = "Sales Order Series"

    def __str__(self):
        return f"{self.name} ({self.prefix})"


class SalesOrder(models.Model):
    """Internal Sales Order, auto-generated when a customer's Purchase Order is confirmed"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name='sales_order')
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)

    series = models.ForeignKey(SalesOrderSeries, on_delete=models.PROTECT, null=True, blank=True)
    sales_order_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_production', 'In Production / Procurement'),
        ('ready_to_dispatch', 'Ready to Dispatch'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if not self.sales_order_number and self.series:
            self.sales_order_number = f"{self.series.prefix}{self.series.next_number:04d}"
            self.series.next_number += 1
            self.series.save()
        super().save(*args, **kwargs)

    def get_subtotal(self):
        return sum(item.get_line_total() for item in self.items.all())

    def __str__(self):
        return f"{self.sales_order_number or 'Draft'} - {self.customer.business_name}"


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    product = ChainedForeignKey(
        Product,
        chained_field="subcategory",
        chained_model_field="subcategory",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def get_line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Unknown'}"


class InvoiceSeries(models.Model):
    """Custom Prefix for Auto-generating Invoice Numbers"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    name = models.CharField(max_length=50, help_text="e.g. FY 26-27 Standard")
    prefix = models.CharField(max_length=20, help_text="e.g. NOA/26-27/")
    next_number = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Invoice Series"
        verbose_name_plural = "Invoice Series"

    def __str__(self):
        return f"{self.name} ({self.prefix})"

class Invoice(models.Model):
    """Tax Invoice linked to Quotation"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    quotation = models.OneToOneField(Quotation, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', help_text="Customer PO this invoice is raised against")
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)

    series = models.ForeignKey(InvoiceSeries, on_delete=models.PROTECT, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    GST_CHOICES = (
        (0.00, '0% GST'),
        (5.00, '5% GST'),
        (12.00, '12% GST'),
        (18.00, '18% GST'),
        (28.00, '28% GST'),
    )
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, choices=GST_CHOICES, default=18.00)
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    def save(self, *args, **kwargs):
        if not self.invoice_number and self.series:
            self.invoice_number = f"{self.series.prefix}{self.series.next_number:04d}"
            self.series.next_number += 1
            self.series.save()
        super().save(*args, **kwargs)
        
    def get_subtotal(self):
        return sum(item.get_line_total() for item in self.items.all())
        
    def get_tax_amount(self):
        return self.get_subtotal() * (self.gst_percent / 100)
        
    def get_grand_total(self):
        return self.get_subtotal() + self.get_tax_amount()
        
    def get_amount_paid(self):
        return sum(payment.amount for payment in self.payments.all())
        
    def get_balance_due(self):
        return self.get_grand_total() - self.get_amount_paid()

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.business_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    product = ChainedForeignKey(
        Product,
        chained_field="subcategory",
        chained_model_field="subcategory",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def get_line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('neft', 'NEFT/RTGS'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    )
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='neft')
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Cheque No. or UTR/UPI Ref")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update invoice status based on balance
        inv = self.invoice
        balance = inv.get_balance_due()
        if balance <= 0:
            inv.status = 'paid'
        elif balance < inv.get_grand_total():
            inv.status = 'partial'
        inv.save()

    def __str__(self):
        return f"{self.amount} for {self.invoice.invoice_number}"

class AMCContract(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    product = ChainedForeignKey(
        Product,
        chained_field="subcategory",
        chained_model_field="subcategory",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    # Generic fields in case of third-party AMC
    third_party_brand = models.CharField(max_length=100, blank=True, help_text="Fill if not NOA product")
    third_party_model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    TYPE_CHOICES = (
        ('comprehensive', 'Comprehensive (Parts & Labor)'),
        ('non_comprehensive', 'Non-Comprehensive (Labor Only)'),
    )
    contract_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='comprehensive')
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('renewed', 'Renewed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    pm_visits_per_year = models.PositiveIntegerField(default=3, help_text="Number of preventive maintenance visits covered")
    auto_generate_tickets = models.BooleanField(default=True, help_text="Automatically schedule PM tickets on save")
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Auto-generate tickets on creation if requested
        if is_new and self.auto_generate_tickets and self.pm_visits_per_year > 0:
            days_interval = 365 // self.pm_visits_per_year
            for i in range(1, self.pm_visits_per_year + 1):
                scheduled_date = self.start_date + timedelta(days=days_interval * i)
                if scheduled_date > self.end_date:
                    scheduled_date = self.end_date - timedelta(days=10) # safety
                    
                ServiceTicket.objects.create(
                    company=self.company,
                    customer=self.customer,
                    division=self.division,
                    category=self.category,
                    subcategory=self.subcategory,
                    product=self.product,
                    amc_contract=self,
                    issue_title=f"Scheduled PM Visit {i}/{self.pm_visits_per_year} for {self.serial_number}",
                    description="Auto-generated Preventive Maintenance visit per AMC Contract.",
                    priority='medium',
                    status='open',
                    ticket_type='pm'
                )

    def __str__(self):
        return f"AMC - {self.customer.business_name} ({self.serial_number})"

class ServiceTicket(models.Model):
    """After-sales support, complaints, and AMC calls"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    category = ChainedForeignKey(
        ProductCategory,
        chained_field="division",
        chained_model_field="division",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    product = ChainedForeignKey(
        Product,
        chained_field="subcategory",
        chained_model_field="subcategory",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    amc_contract = models.ForeignKey(AMCContract, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    
    TICKET_TYPE_CHOICES = (
        ('complaint', 'Complaint / Breakdown'),
        ('installation', 'New Installation'),
        ('pm', 'Preventive Maintenance (AMC)'),
        ('paid', 'Paid Service Call'),
    )
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='complaint')
    
    issue_title = models.CharField(max_length=255)
    description = models.TextField()
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    assigned_engineer = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user__role__name': 'Engineer'})
    resolution_notes = models.TextField(blank=True, null=True, help_text="Internal notes by engineer")
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.issue_title}"
