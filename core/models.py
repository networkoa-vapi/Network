from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
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

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marriage_anniversary = models.DateField(null=True, blank=True, help_text="Leave blank if not applicable")

    present_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)

    # Bank Details
    bank_account_holder_name = models.CharField(max_length=150, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    bank_ifsc_code = models.CharField(max_length=15, blank=True)
    bank_name = models.CharField(max_length=150, blank=True)
    bank_branch = models.CharField(max_length=150, blank=True)

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


class EmployeeFamilyMember(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=150)
    RELATION_CHOICES = (
        ('spouse', 'Spouse'),
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
        ('sibling', 'Sibling'),
        ('other', 'Other'),
    )
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Family Member"
        verbose_name_plural = "Family Details"

    def __str__(self):
        return f"{self.name} ({self.get_relation_display()})"


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    DOCUMENT_TYPE_CHOICES = (
        ('degree_certificate', 'Degree Certificate'),
        ('experience_letter', 'Experience Letter'),
        ('aadhar_card', 'Aadhar Card'),
        ('driving_licence', 'Driving Licence'),
        ('bank_proof', 'Bank Proof / Cancelled Cheque'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Employee Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.employee}"


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
        ('repeat_order', 'Repeat Order'),
        ('oem_lead', 'OEM Lead'),
        ('direct_sales', 'Direct Sales'),
        ('tender', 'Tender'),
        ('showroom', 'Show Room'),
        ('online_platform', 'Online Platform'),
        ('architect_lead', 'Architect Lead'),
        ('other', 'Other'),
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='email')

    SALE_TYPE_CHOICES = (
        ('direct', 'Direct Sales'),
        ('project', 'Project Sales'),
    )
    sale_type = models.CharField(max_length=10, choices=SALE_TYPE_CHOICES, default='direct', help_text="Direct Sales (retail/standard) or Project Sales (large/contracted projects)")

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

            sales_order.project.generate_purchase_requisition()

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

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not hasattr(self, 'project'):
            # Purchase Requisition generation is deferred to PurchaseOrder.save(), which
            # creates this SalesOrder's line items right after calling SalesOrder.objects.create() -
            # generating the PR here would run before any items exist to compare against stock.
            Project.objects.create(
                company=self.company,
                sales_order=self,
                customer=self.customer,
                name=f"Project - {self.customer.business_name} ({self.sales_order_number or self.pk})",
            )

    def get_subtotal(self):
        return sum(item.get_line_total() for item in self.items.all())

    def get_material_consumption(self):
        """Per stock item on this project: issued vs. returned vs. net consumed (billable to the party)."""
        rows = []
        item_ids = self.stock_transactions.values_list('stock_item_id', flat=True).distinct()
        for stock_item in StockItem.objects.filter(pk__in=item_ids):
            qs = self.stock_transactions.filter(stock_item=stock_item)
            issued = qs.filter(transaction_type='issue').aggregate(t=models.Sum('quantity'))['t'] or 0
            returned = qs.filter(transaction_type='return').aggregate(t=models.Sum('quantity'))['t'] or 0
            rows.append({
                'stock_item': stock_item,
                'issued': issued,
                'returned': returned,
                'consumed': issued - returned,
            })
        return rows

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


# ─────────────────────────────────────────────────────────────
# Service Hub - Equipment Registration & AMC Coverage
# ─────────────────────────────────────────────────────────────

class AMCCoverageItem(models.Model):
    """Master list of things that can be covered under an AMC (e.g. Compressor, PCB, Gas Charging, Labor)."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "AMC Coverage Item"
        verbose_name_plural = "AMC Coverage Items"
        ordering = ['name']

    def __str__(self):
        return self.name


class Equipment(models.Model):
    """Asset register: every piece of equipment installed at a customer site, tracked across its lifetime."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='equipment')
    asset_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name="NOA Asset Number")

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    category = ChainedForeignKey(
        ProductCategory, chained_field="division", chained_model_field="division",
        show_all=False, auto_choose=True, sort=True, on_delete=models.SET_NULL, null=True, blank=True
    )
    subcategory = ChainedForeignKey(
        ProductSubCategory, chained_field="category", chained_model_field="category",
        show_all=False, auto_choose=True, sort=True, on_delete=models.SET_NULL, null=True, blank=True
    )
    product = ChainedForeignKey(
        Product, chained_field="subcategory", chained_model_field="subcategory",
        show_all=False, auto_choose=True, sort=True, on_delete=models.SET_NULL, null=True, blank=True
    )

    third_party_brand = models.CharField(max_length=100, blank=True, help_text="Fill if not a NOA-sold product")
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100)
    model_description = models.TextField(blank=True)
    installation_date = models.DateField(null=True, blank=True)
    installation_site = models.CharField(max_length=255, blank=True, help_text="Site / location address (a customer can have equipment at multiple sites)")

    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)

    AMC_TYPE_CHOICES = (
        ('none', 'No AMC'),
        ('comprehensive', 'Comprehensive (Parts & Labor)'),
        ('non_comprehensive', 'Non-Comprehensive (Labor Only)'),
    )
    amc_type = models.CharField(max_length=30, choices=AMC_TYPE_CHOICES, default='none')
    amc_start_date = models.DateField(null=True, blank=True)
    amc_end_date = models.DateField(null=True, blank=True)
    services_per_period = models.PositiveIntegerField(default=0, help_text="No. of services covered under the AMC period")
    amc_coverage_items = models.ManyToManyField(AMCCoverageItem, blank=True, related_name='equipment', help_text="What is covered under the AMC for this equipment")

    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.asset_number:
            import uuid
            self.asset_number = f"NOA-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.asset_number} - {self.customer.business_name} ({self.serial_number})"


class EquipmentPartReplacement(models.Model):
    """Log of parts replaced on an equipment, keeping the same Asset record instead of registering a new one."""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='part_replacements')
    stock_item = models.ForeignKey('StockItem', on_delete=models.PROTECT, related_name='+')
    service_ticket = models.ForeignKey('ServiceTicket', on_delete=models.SET_NULL, null=True, blank=True, related_name='part_replacements')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)

    REPLACED_UNDER_CHOICES = (
        ('warranty', 'Under Warranty'),
        ('amc', 'Under AMC'),
        ('chargeable', 'Chargeable'),
    )
    replaced_under = models.CharField(max_length=20, choices=REPLACED_UNDER_CHOICES, default='warranty')
    replaced_date = models.DateField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Part Replacement"
        verbose_name_plural = "Part Replacements"
        ordering = ['-replaced_date']

    def __str__(self):
        return f"{self.stock_item.name} on {self.equipment.asset_number}"


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
    ticket_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets', help_text="The registered asset this complaint is against, if known")
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

    # ── How the complaint came in ───────────────────────────
    RECEIVED_VIA_CHOICES = (
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('when_visited', 'When Visited'),
        ('reach_another', 'When Reached for Another Problem'),
        ('oem', 'By OEM'),
        ('whatsapp', "By WhatsApp"),
    )
    received_via = models.CharField(max_length=20, choices=RECEIVED_VIA_CHOICES, default='phone')
    reported_by_name = models.CharField(max_length=150, blank=True, help_text="Name of the person who reported the complaint (if different from the registered customer contact)")
    reported_by_mobile = models.CharField(max_length=20, blank=True)

    TICKET_TYPE_CHOICES = (
        ('warranty', 'Under Warranty'),
        ('amc', 'Under AMC'),
        ('chargeable', 'Chargeable Call'),
        ('foc', 'Free of Charge (FOC)'),
        ('installation', 'New Installation'),
        ('pm', 'Preventive Maintenance (AMC)'),
    )
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='chargeable', verbose_name="Complaint Type")

    PROBLEM_TYPE_CHOICES = (
        ('not_working', "Equipment Doesn't Work"),
        ('shows_error', 'Equipment Shows Error'),
        ('water_leakage', 'Water Leakage Problem'),
        ('no_cooling', 'Not Cooling Properly'),
        ('compressor_fail', 'Compressor Fail'),
        ('remote_problem', 'Remote Control Problem'),
        ('gas_leakage', 'Gas Leakage'),
        ('service_required', 'Service Required'),
        ('abnormal_sound', 'Equipment Sound Abnormal'),
        ('idu_not_working', 'IDU Not Working'),
        ('odu_not_working', 'ODU Not Working'),
        ('water_cooler_not_cooling', 'Water Not Cooling in Water Cooler'),
        ('deep_freezer_temp', 'Temperature Not Achieving in Deep Freezer'),
        ('ice_formation', 'Ice Formation'),
        ('improper_installation', 'Installation Not Properly Done'),
        ('other', 'Other'),
    )
    problem_type = models.CharField(max_length=30, choices=PROBLEM_TYPE_CHOICES, blank=True)

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

    # ── Outcome after the visit ──────────────────────────────
    OUTCOME_CHOICES = (
        ('', 'Not Yet Attended'),
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    )
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, blank=True)

    PENDING_REASON_CHOICES = (
        ('other_complaint', 'Not Reached Due to Other Complaint Not Completed'),
        ('no_power', 'No Power at Site'),
        ('incomplete_safety', 'Due to Incomplete Safety Arrangement from Our Side'),
        ('parts_unavailable', 'Due to Parts Unavailability'),
        ('quotation_confirmation', 'Required to Give Quotation & Take Confirmation'),
        ('half_work_done', 'Due to Half Work Done'),
    )
    pending_reason = models.CharField(max_length=30, choices=PENDING_REASON_CHOICES, blank=True)

    assigned_engineers = models.ManyToManyField(
        'Employee', blank=True, related_name='assigned_tickets',
        limit_choices_to={'user__role__name': 'Engineer'},
        help_text="Multiple technicians can be allocated to a single job"
    )
    resolution_notes = models.TextField(blank=True, null=True, help_text="Internal / technician remarks")
    customer_remarks = models.TextField(blank=True, help_text="Remarks or feedback from the customer")

    call_start_time = models.DateTimeField(blank=True, null=True)
    call_close_time = models.DateTimeField(blank=True, null=True)
    service_call_report = models.FileField(upload_to='service_reports/', blank=True, null=True, help_text="Required before the ticket can be closed")

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Service Ticket"
        verbose_name_plural = "Service Tickets"
        ordering = ['-created_at']

    def clean(self):
        if self.outcome == 'pending' and not self.pending_reason:
            raise ValidationError("Please select a reason why this complaint is pending.")
        if self.status in ('resolved', 'closed'):
            if self.outcome == 'pending':
                raise ValidationError("This ticket is marked 'Pending' - it cannot be Resolved/Closed until the outcome is 'Completed'.")
            if not self.service_call_report:
                raise ValidationError("A Service Call Report must be uploaded before this ticket can be Resolved/Closed.")
            if not self.call_close_time:
                raise ValidationError("Call Close Time is required before this ticket can be Resolved/Closed.")

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import uuid
            self.ticket_number = f"TCK-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number or ('#' + str(self.id))} - {self.issue_title}"


class ServiceTicketPartUsed(models.Model):
    """Parts consumed/replaced while resolving a Service Ticket - issued from Store stock."""
    ticket = models.ForeignKey(ServiceTicket, on_delete=models.CASCADE, related_name='parts_used')
    stock_item = models.ForeignKey('StockItem', on_delete=models.PROTECT, related_name='+')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Part Used"
        verbose_name_plural = "Parts Used"

    def __str__(self):
        return f"{self.quantity} x {self.stock_item.name}"


# ─────────────────────────────────────────────────────────────
# Store / Inventory Management Module
# Main Godown -> Sub Godown stock transfers, and material issue
# to parties (employees / customers-sites / other).
# ─────────────────────────────────────────────────────────────

class Godown(models.Model):
    """A physical stock location. Sub Godowns receive stock transferred from a Main Godown."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)

    GODOWN_TYPE_CHOICES = (
        ('main', 'Main Godown'),
        ('sub', 'Sub Godown'),
    )
    godown_type = models.CharField(max_length=10, choices=GODOWN_TYPE_CHOICES, default='main')
    parent_godown = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sub_godowns',
        limit_choices_to={'godown_type': 'main'},
        help_text="For a Sub Godown, the Main Godown it receives stock from."
    )

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, help_text="Site / address of this godown")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Godown"
        verbose_name_plural = "Godowns"
        ordering = ['godown_type', 'name']

    def clean(self):
        if self.godown_type == 'main' and self.parent_godown:
            raise ValidationError("A Main Godown cannot have a parent Godown.")
        if self.godown_type == 'sub' and self.parent_godown_id == self.pk:
            raise ValidationError("A Godown cannot be its own parent.")

    def __str__(self):
        return f"{self.name} ({self.get_godown_type_display()})"


class StockCategory(models.Model):
    """Store item category (e.g. Tools, Capital Goods) — managed from the Store admin, not hardcoded."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Stock Category"
        verbose_name_plural = "Stock Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class StockSubCategory(models.Model):
    """Sub-category under a Stock Category (e.g. Tools -> Issued to Technical Staff). Optional - not every category needs one."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    category = models.ForeignKey(StockCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Stock Sub-Category"
        verbose_name_plural = "Stock Sub-Categories"
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class StockItem(models.Model):
    """Store item master — every physical item type the Store department keeps stock of."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)

    category = models.ForeignKey(StockCategory, on_delete=models.PROTECT, related_name='stock_items')
    subcategory = ChainedForeignKey(
        StockSubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_items',
        help_text="Only shown if the selected category has sub-categories"
    )

    UNIT_CHOICES = (
        ('nos', 'Nos'),
        ('kg', 'Kg'),
        ('litre', 'Litre'),
        ('box', 'Box'),
        ('set', 'Set'),
        ('meter', 'Meter'),
        ('pair', 'Pair'),
        ('roll', 'Roll'),
        ('other', 'Other'),
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='nos')

    name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=100, unique=True, help_text="Internal store code for this item")
    linked_product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Link to the Sales catalog Product, if this is a sellable 'Goods for Sale' item"
    )
    reorder_level = models.PositiveIntegerField(default=0, help_text="Alert when total stock falls to/below this level")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Stock Item"
        verbose_name_plural = "Stock Items"
        ordering = ['name']

    def get_stock_balance(self, godown=None, exclude_pk=None):
        qs = self.transactions.all()
        if godown is not None:
            qs = qs.filter(godown=godown)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        inbound = qs.filter(transaction_type__in=StockTransaction.INBOUND_TYPES).aggregate(total=models.Sum('quantity'))['total'] or 0
        outbound = qs.filter(transaction_type__in=StockTransaction.OUTBOUND_TYPES).aggregate(total=models.Sum('quantity'))['total'] or 0
        return inbound - outbound

    def __str__(self):
        return f"{self.item_code} - {self.name}"


class StockTransaction(models.Model):
    """Ledger of every stock movement: receipts, Main->Sub transfers, issues, and returns."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    voucher_number = models.CharField(max_length=50, unique=True, blank=True)

    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name='transactions')
    godown = models.ForeignKey(Godown, on_delete=models.PROTECT, related_name='transactions', help_text="Godown this transaction is recorded against")
    sales_order = models.ForeignKey(
        SalesOrder, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_transactions',
        help_text="Project (Sales Order) this material was issued for / returned from"
    )

    TRANSACTION_TYPE_CHOICES = (
        ('receipt', 'Stock Receipt (Inward / Purchase)'),
        ('transfer_in', 'Transfer In (from Main Godown)'),
        ('return', 'Returned to Store'),
        ('adjustment_in', 'Stock Adjustment - Increase'),
        ('transfer_out', 'Transfer Out (to Sub Godown)'),
        ('issue', 'Issued to Party'),
        ('scrap', 'Scrapped / Written Off'),
        ('adjustment_out', 'Stock Adjustment - Decrease'),
    )
    INBOUND_TYPES = ['receipt', 'transfer_in', 'return', 'adjustment_in']
    OUTBOUND_TYPES = ['transfer_out', 'issue', 'scrap', 'adjustment_out']

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    destination_godown = models.ForeignKey(
        Godown, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='incoming_transfers',
        help_text="For 'Transfer Out': the Sub Godown receiving this stock"
    )

    PARTY_TYPE_CHOICES = (
        ('employee', 'Employee'),
        ('customer', 'Customer / Site'),
        ('other', 'Other / External Party'),
    )
    party_type = models.CharField(max_length=10, choices=PARTY_TYPE_CHOICES, blank=True)
    issued_to_employee = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_issues')
    issued_to_customer = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_issues')
    party_name = models.CharField(max_length=255, blank=True, help_text="Free-text party/site name (used when party type is 'Other', or as extra detail)")

    related_transaction = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='return_transactions',
        limit_choices_to={'transaction_type': 'issue'},
        help_text="For a 'Return' transaction: which Issue voucher this is returning against"
    )

    transaction_date = models.DateField(auto_now_add=True)
    handled_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_transactions_handled')
    remarks = models.TextField(blank=True)

    VOUCHER_PREFIXES = {
        'receipt': 'GRN', 'transfer_in': 'TRF', 'return': 'RET', 'adjustment_in': 'ADJ',
        'transfer_out': 'TRF', 'issue': 'ISS', 'scrap': 'SCR', 'adjustment_out': 'ADJ',
    }

    class Meta:
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"
        ordering = ['-transaction_date', '-id']

    def clean(self):
        if self.transaction_type == 'transfer_out' and not self.destination_godown:
            raise ValidationError("Transfer Out requires a destination Sub Godown.")
        if self.transaction_type == 'return' and not self.related_transaction:
            raise ValidationError("A Return transaction must reference the original Issue voucher.")
        if self.stock_item_id and self.godown_id and self.transaction_type in self.OUTBOUND_TYPES:
            available = self.stock_item.get_stock_balance(godown=self.godown, exclude_pk=self.pk)
            if self.quantity and self.quantity > available:
                raise ValidationError(f"Only {available} {self.stock_item.get_unit_display()} of {self.stock_item.name} available at {self.godown.name}.")

    def save(self, *args, **kwargs):
        if not self.voucher_number:
            import uuid
            prefix = self.VOUCHER_PREFIXES.get(self.transaction_type, 'STK')
            self.voucher_number = f"{prefix}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.voucher_number} - {self.get_transaction_type_display()} - {self.stock_item.name} ({self.quantity})"


# ─────────────────────────────────────────────────────────────
# Project Department
# ─────────────────────────────────────────────────────────────

class Project(models.Model):
    """Auto-created whenever a Sales Order is generated; tracks execution and material procurement."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, related_name='project', null=True, blank=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)

    project_number = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=255)

    STATUS_CHOICES = (
        ('planning', 'Planning'),
        ('procurement', 'Procurement'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')

    start_date = models.DateField(auto_now_add=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.project_number:
            import uuid
            self.project_number = f"PRJ-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def generate_purchase_requisition(self):
        """Auto-create a PR from this project's Sales Order items, matched to Store stock items and compared against current stock."""
        if not self.sales_order:
            return None
        pr = PurchaseRequisition.objects.create(company=self.company, project=self)
        for so_item in self.sales_order.items.all():
            if not so_item.product:
                continue
            stock_item = StockItem.objects.filter(linked_product=so_item.product, is_active=True).first()
            if stock_item:
                PurchaseRequisitionItem.objects.create(
                    purchase_requisition=pr,
                    stock_item=stock_item,
                    quantity=so_item.quantity,
                )
        return pr

    def __str__(self):
        return f"{self.project_number} - {self.customer.business_name}"


class PurchaseRequisition(models.Model):
    """Materials needed for a Project. Each line flags whether current stock covers it or it needs purchasing."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='purchase_requisitions')

    pr_number = models.CharField(max_length=50, unique=True, blank=True)

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Purchase'),
        ('ordered', 'Ordered'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    requested_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = "Purchase Requisition"
        verbose_name_plural = "Purchase Requisitions"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pr_number:
            import uuid
            self.pr_number = f"PR-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def get_shortfall_items(self):
        return [item for item in self.items.all() if item.is_shortfall]

    def has_shortfall(self):
        return len(self.get_shortfall_items()) > 0

    def __str__(self):
        return f"{self.pr_number} - {self.project.project_number}"


class PurchaseRequisitionItem(models.Model):
    purchase_requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name='items')
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name='requisition_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)

    # Workflow status, separate from the live shortfall calculation below (which always
    # reflects *current* stock). This tracks which department has actioned the line:
    # Store issues items already in stock; Purchase procures items that are short.
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('issued', 'Issued from Stock'),
        ('ordered', 'Purchase Ordered'),
        ('received', 'Received / Fulfilled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def get_current_stock(self):
        return self.stock_item.get_stock_balance()

    @property
    def is_shortfall(self):
        return self.quantity > self.get_current_stock()

    @property
    def shortfall_qty(self):
        remaining = self.quantity - self.get_current_stock()
        return remaining if remaining > 0 else 0

    @property
    def recommended_purchase_qty(self):
        """While we're already short and placing an order, top up to the item's
        Minimum Stock Level (reorder_level) too, not just cover this requisition."""
        if not self.is_shortfall:
            return 0
        return self.shortfall_qty + self.stock_item.reorder_level

    def __str__(self):
        return f"{self.quantity} x {self.stock_item.name}"


# ─────────────────────────────────────────────────────────────
# Purchase Department - Suppliers, Price Comparison, Purchase Orders
# ─────────────────────────────────────────────────────────────

class Supplier(models.Model):
    """Vendor/supplier master - lives under Master, shared across the whole system."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Include country code, e.g. +919876543210")
    alternate_contact_person = models.CharField(max_length=255, blank=True)
    alternate_contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=15, blank=True, verbose_name="GSTIN")
    pan_number = models.CharField(max_length=10, blank=True, verbose_name="PAN Number")
    tan_number = models.CharField(max_length=10, blank=True, verbose_name="TAN Number")
    payment_terms = models.CharField(max_length=255, blank=True, help_text="e.g. 50% advance, balance on delivery / Net 30")
    deals_in_items = models.ManyToManyField(
        'StockItem', blank=True, related_name='suppliers',
        help_text="Items this supplier deals in - also used to search/filter suppliers by item."
    )

    # Bank Details
    bank_account_holder_name = models.CharField(max_length=150, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    bank_ifsc_code = models.CharField(max_length=15, blank=True)
    bank_name = models.CharField(max_length=150, blank=True)
    bank_branch = models.CharField(max_length=150, blank=True)

    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']

    def __str__(self):
        return self.name


class SupplierQuote(models.Model):
    """Price comparison: log multiple supplier quotes against one Purchase Requisition line, then mark the winner."""
    purchase_requisition_item = models.ForeignKey(PurchaseRequisitionItem, on_delete=models.CASCADE, related_name='supplier_quotes')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='quotes')
    quoted_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price per unit")
    quoted_date = models.DateField(auto_now_add=True)
    delivery_days = models.PositiveIntegerField(null=True, blank=True, help_text="Expected delivery time in days")
    is_selected = models.BooleanField(default=False, help_text="Mark the chosen supplier for this item")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Supplier Quote"
        verbose_name_plural = "Supplier Quotes"
        ordering = ['quoted_price']

    def get_total(self):
        return self.quoted_price * self.purchase_requisition_item.quantity

    def __str__(self):
        return f"{self.supplier.name} - {self.quoted_price}/unit"


class SupplierPurchaseOrder(models.Model):
    """Our Purchase Order sent to a Supplier/Vendor - distinct from the customer's PurchaseOrder to us."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=get_default_company)
    po_number = models.CharField(max_length=50, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='supplier_purchase_orders')

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent to Supplier'),
        ('confirmed', 'Confirmed by Supplier'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = "Purchase Order (Supplier)"
        verbose_name_plural = "Purchase Orders (Supplier)"
        ordering = ['-order_date']

    def save(self, *args, **kwargs):
        if not self.po_number:
            import uuid
            self.po_number = f"SPO-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def get_grand_total(self):
        return sum(item.get_line_total() for item in self.items.all())

    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"


class SupplierPurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(SupplierPurchaseOrder, on_delete=models.CASCADE, related_name='items')
    requisition_item = models.ForeignKey(
        PurchaseRequisitionItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='po_items',
        help_text="Which Purchase Requisition line this fulfills, if any"
    )
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Auto-filled from the selected supplier quote for this line, if any")

    def save(self, *args, **kwargs):
        if not self.unit_price and self.requisition_item:
            quote = self.requisition_item.supplier_quotes.filter(supplier=self.purchase_order.supplier, is_selected=True).first()
            if quote:
                self.unit_price = quote.quoted_price
        super().save(*args, **kwargs)

    def get_line_total(self):
        return self.quantity * (self.unit_price or 0)

    def __str__(self):
        return f"{self.quantity} x {self.stock_item.name}"
