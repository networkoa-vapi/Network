import os

base_dir = r"c:\Network"
apps = {
    "sales": {
        "verbose_name": "Sales & CRM",
        "models": {
            "Inquiry": ("InquiryAdmin", "Inquiries"),
            "Quotation": ("QuotationAdmin", "Quotations"),
            "Invoice": ("InvoiceAdmin", "Invoices"),
            "CustomerProfile": ("CustomerProfileAdmin", "Customer Profiles"),
        }
    },
    "service": {
        "verbose_name": "Service Department",
        "models": {
            "ServiceTicket": ("ServiceTicketAdmin", "Service Tickets"),
            "AMCContract": ("AMCContractAdmin", "AMC Contracts"),
        }
    },
    "inventory": {
        "verbose_name": "Product Master",
        "models": {
            "Product": ("ProductAdmin", "Products"),
            "ProductCategory": ("ProductCategoryAdmin", "Product Categories"),
            "ProductDocument": ("ProductDocumentAdmin", "Product Documents"),
        }
    }
}

for app_name, app_data in apps.items():
    app_dir = os.path.join(base_dir, app_name)
    os.makedirs(app_dir, exist_ok=True)
    
    # __init__.py
    with open(os.path.join(app_dir, "__init__.py"), "w") as f:
        pass
        
    # apps.py
    with open(os.path.join(app_dir, "apps.py"), "w") as f:
        f.write(f"from django.apps import AppConfig\n\nclass {app_name.capitalize()}Config(AppConfig):\n    name = '{app_name}'\n    verbose_name = '{app_data['verbose_name']}'\n")

    # models.py
    with open(os.path.join(app_dir, "models.py"), "w") as f:
        f.write("from core.models import " + ", ".join(app_data['models'].keys()) + "\n\n")
        for model_name, (_, plural) in app_data['models'].items():
            f.write(f"class {app_name.capitalize()}{model_name}({model_name}):\n")
            f.write(f"    class Meta:\n")
            f.write(f"        proxy = True\n")
            f.write(f"        app_label = '{app_name}'\n")
            f.write(f"        verbose_name = '{model_name}'\n")
            f.write(f"        verbose_name_plural = '{plural}'\n\n")
            
    # admin.py
    with open(os.path.join(app_dir, "admin.py"), "w") as f:
        f.write("from django.contrib import admin\n")
        f.write("from .models import " + ", ".join([f"{app_name.capitalize()}{m}" for m in app_data['models'].keys()]) + "\n")
        f.write("from core.admin import " + ", ".join([v[0] for v in app_data['models'].values()]) + "\n\n")
        for model_name, (admin_class, _) in app_data['models'].items():
            f.write(f"admin.site.register({app_name.capitalize()}{model_name}, {admin_class})\n")
