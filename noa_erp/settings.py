"""
Django settings for NOA ERP project.
"""

import os
from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-noa-erp-change-me-in-production-!@#$%^&*()'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # Unfold re-skins the Django admin as a modern SaaS console. It works by
    # overriding admin templates, so every 'unfold*' entry must sit ABOVE
    # 'django.contrib.admin' for its templates to win the lookup.
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'unfold.contrib.import_export',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'core',
    'sales',
    'service',
    'inventory',
    'store',
    'purchase',
    'project',
    'hr',
    'smart_selects',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'noa_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'noa_erp.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db2.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (User uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'


# ── Unfold admin theme ──────────────────────────────────────────────
# Replaces the stock Django admin skin with a modern SaaS console.

def _perm(codename):
    """Sidebar visibility check for one model.

    The stock admin sidebar hides models the user can't view automatically;
    because the navigation below is declared by hand, each entry has to carry
    that check itself or staff would see links that 403 on click.

    IMPORTANT: use the PROXY model's permission, not the concrete core one. Every
    department screen is registered as a proxy (sales.SalesInvoice, not
    core.Invoice), and Django creates and grants permissions under the proxy's own
    app label. The role groups therefore hold 'sales.view_salesinvoice' and never
    'core.view_invoice' - guarding on the latter hides the entry from everyone
    except superusers, who skip the check entirely and so never see the bug.
    """
    return lambda request: request.user.has_perm(codename)


def _link(viewname):
    return reverse_lazy(viewname)


UNFOLD = {
    'SITE_TITLE': 'NOA ERP',
    'SITE_HEADER': 'NOA ERP',
    'SITE_SUBHEADER': 'Network Office Automation',
    'SITE_URL': '/',
    'SITE_SYMBOL': 'apartment',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': False,
    'SHOW_BACK_BUTTON': True,

    'SITE_ICON': {
        'light': lambda request: static('company_logos/noa_icon.png'),
        'dark': lambda request: static('company_logos/noa_icon.png'),
    },
    'SITE_LOGO': {
        'light': lambda request: static('company_logos/noa_erp_logo_v2.png'),
        # The stock lockup is dark indigo ink and disappears on the dark
        # sidebar, so dark mode gets the white-ink variant.
        'dark': lambda request: static('company_logos/noa_erp_logo_dark.png'),
    },

    'LOGIN': {
        'image': lambda request: static('company_logos/noa_erp_logo_v2.png'),
    },

    # Brand palette taken from the NOA logo itself (indigo wordmark + blue
    # globe) rather than the teal the old stylesheet used, which fought it.
    'COLORS': {
        'base': {
            '50': 'oklch(98.4% .003 247.858)',
            '100': 'oklch(96.8% .007 247.896)',
            '200': 'oklch(92.9% .013 255.508)',
            '300': 'oklch(86.9% .022 252.894)',
            '400': 'oklch(70.4% .04 256.788)',
            '500': 'oklch(55.4% .046 257.417)',
            '600': 'oklch(44.6% .043 257.281)',
            '700': 'oklch(37.2% .044 257.287)',
            '800': 'oklch(27.9% .041 260.031)',
            '900': 'oklch(20.8% .042 265.755)',
            '950': 'oklch(12.9% .042 264.695)',
        },
        'primary': {
            '50': 'oklch(96.2% .018 272.314)',
            '100': 'oklch(93% .034 272.788)',
            '200': 'oklch(87% .065 274.039)',
            '300': 'oklch(78.5% .115 274.713)',
            '400': 'oklch(67.3% .182 276.935)',
            '500': 'oklch(58.5% .233 277.117)',
            '600': 'oklch(51.1% .262 276.966)',
            '700': 'oklch(45.7% .24 277.023)',
            '800': 'oklch(39.8% .195 277.366)',
            '900': 'oklch(35.9% .144 278.697)',
            '950': 'oklch(25.7% .09 281.288)',
        },
    },

    'BORDER_RADIUS': '8px',

    'DASHBOARD_CALLBACK': 'core.dashboard.dashboard_callback',

    'STYLES': [
        lambda request: static('css/unfold_noa.css'),
    ],

    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': 'Overview',
                'separator': False,
                'items': [
                    {'title': 'Dashboard', 'icon': 'dashboard',
                     'link': _link('admin:index')},
                    {'title': 'Reports Center', 'icon': 'analytics',
                     'link': _link('reports_center')},
                ],
            },
            {
                'title': 'Sales & CRM',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': 'Inquiries', 'icon': 'contact_support',
                     'link': _link('admin:sales_salesinquiry_changelist'),
                     'permission': _perm('sales.view_salesinquiry')},
                    {'title': 'Quotations', 'icon': 'request_quote',
                     'link': _link('admin:sales_salesquotation_changelist'),
                     'permission': _perm('sales.view_salesquotation')},
                    {'title': 'Customer POs', 'icon': 'receipt_long',
                     'link': _link('admin:sales_salespurchaseorder_changelist'),
                     'permission': _perm('sales.view_salespurchaseorder')},
                    {'title': 'Sales Orders', 'icon': 'shopping_cart',
                     'link': _link('admin:sales_salesorder_changelist'),
                     'permission': _perm('sales.view_salesorder')},
                    {'title': 'Invoices', 'icon': 'receipt',
                     'link': _link('admin:sales_salesinvoice_changelist'),
                     'permission': _perm('sales.view_salesinvoice')},
                    {'title': 'Customers', 'icon': 'groups',
                     'link': _link('admin:sales_salescustomerprofile_changelist'),
                     'permission': _perm('sales.view_salescustomerprofile')},
                ],
            },
            {
                'title': 'Projects',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': 'Projects', 'icon': 'workspaces',
                     'link': _link('admin:project_project_changelist'),
                     'permission': _perm('project.view_project')},
                    {'title': 'Purchase Requisitions', 'icon': 'assignment',
                     'link': _link('admin:project_purchaserequisition_changelist'),
                     'permission': _perm('project.view_purchaserequisition')},
                ],
            },
            {
                'title': 'Service',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': 'Equipment', 'icon': 'precision_manufacturing',
                     'link': _link('admin:service_serviceequipment_changelist'),
                     'permission': _perm('service.view_serviceequipment')},
                    {'title': 'Service Tickets', 'icon': 'build',
                     'link': _link('admin:service_serviceserviceticket_changelist'),
                     'permission': _perm('service.view_serviceserviceticket')},
                    {'title': 'Pending Complaints', 'icon': 'priority_high',
                     'link': _link('admin:service_pendingcomplaints_changelist'),
                     'permission': _perm('service.view_pendingcomplaints')},
                    {'title': 'AMC Contracts', 'icon': 'handshake',
                     'link': _link('admin:service_serviceamccontract_changelist'),
                     'permission': _perm('service.view_serviceamccontract')},
                ],
            },
            {
                'title': 'Store & Stock',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': 'Stock Items', 'icon': 'inventory_2',
                     'link': _link('admin:store_storestockitem_changelist'),
                     'permission': _perm('store.view_storestockitem')},
                    {'title': 'Purchase Inward', 'icon': 'call_received',
                     'link': _link('admin:store_purchaseinward_changelist'),
                     'permission': _perm('store.view_purchaseinward')},
                    {'title': 'Material Issue', 'icon': 'call_made',
                     'link': _link('admin:store_materialissue_changelist'),
                     'permission': _perm('store.view_materialissue')},
                    {'title': 'Items to Issue', 'icon': 'pending_actions',
                     'link': _link('admin:store_itemstoissue_changelist'),
                     'permission': _perm('store.view_itemstoissue')},
                    {'title': 'Pending Returnables', 'icon': 'assignment_return',
                     'link': _link('admin:store_pendingreturnableitems_changelist'),
                     'permission': _perm('store.view_pendingreturnableitems')},
                    {'title': 'Refill Entries', 'icon': 'autorenew',
                     'link': _link('admin:store_refillentry_changelist'),
                     'permission': _perm('store.view_refillentry')},
                    {'title': 'Godowns', 'icon': 'warehouse',
                     'link': _link('admin:store_storegodown_changelist'),
                     'permission': _perm('store.view_storegodown')},
                ],
            },
            {
                'title': 'Purchase',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': 'Items to Purchase', 'icon': 'shopping_bag',
                     'link': _link('admin:purchase_itemstopurchase_changelist'),
                     'permission': _perm('purchase.view_itemstopurchase')},
                    {'title': 'Supplier POs', 'icon': 'local_shipping',
                     'link': _link('admin:purchase_supplierpurchaseorder_changelist'),
                     'permission': _perm('purchase.view_supplierpurchaseorder')},
                ],
            },
            {
                'title': 'HR',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': 'Employees', 'icon': 'badge',
                     'link': _link('admin:hr_hremployee_changelist'),
                     'permission': _perm('hr.view_hremployee')},
                    {'title': 'Offer Letters', 'icon': 'description',
                     'link': _link('admin:hr_hrofferletter_changelist'),
                     'permission': _perm('hr.view_hrofferletter')},
                ],
            },
            {
                'title': 'Master Setup',
                'separator': True,
                'collapsible': True,
                'items': [
                    {'title': 'Products', 'icon': 'category',
                     'link': _link('admin:inventory_inventoryproduct_changelist'),
                     'permission': _perm('inventory.view_inventoryproduct')},
                    {'title': 'Suppliers', 'icon': 'store',
                     'link': _link('admin:core_supplier_changelist'),
                     'permission': _perm('core.view_supplier')},
                    {'title': 'Company', 'icon': 'apartment',
                     'link': _link('admin:core_company_changelist'),
                     'permission': _perm('core.view_company')},
                    {'title': 'Users', 'icon': 'manage_accounts',
                     'link': _link('admin:core_user_changelist'),
                     'permission': _perm('core.view_user')},
                    {'title': 'Roles & Permissions', 'icon': 'admin_panel_settings',
                     'link': _link('admin:auth_group_changelist'),
                     'permission': _perm('auth.view_group')},
                ],
            },
        ],
    },
}
