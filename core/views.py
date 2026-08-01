from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Quotation, ServiceTicket, CustomerProfile, Company, Product, Division, ProductCategory, ProductSubCategory
from django.http import HttpResponseForbidden

def is_customer(user):
    return user.is_authenticated and user.role and user.role.name == 'Customer'

def is_engineer(user):
    return user.is_authenticated and user.role and user.role.name == 'Engineer'

def portal_login(request):
    if request.user.is_authenticated:
        if request.user.role and request.user.role.name == 'Customer':
            return redirect('dashboard')
        elif request.user.role and request.user.role.name == 'Engineer':
            return redirect('engineer_dashboard')
        else:
            return redirect('/admin/')
            
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if user.role and user.role.name == 'Customer':
                login(request, user)
                return redirect('dashboard')
            elif user.role and user.role.name == 'Engineer':
                login(request, user)
                return redirect('engineer_dashboard')
            else:
                login(request, user)
                return redirect('/admin/')
        else:
            messages.error(request, 'Invalid credentials.')
            
    return render(request, 'portal/login.html')

def portal_logout(request):
    logout(request)
    return redirect('portal_login')

@login_required
def dashboard(request):
    if not is_customer(request.user): return redirect('/admin/')
    
    try:
        profile = request.user.customerprofile
    except:
        return HttpResponseForbidden("Customer profile not found.")
        
    tickets_count = ServiceTicket.objects.filter(customer=profile).exclude(status='closed').count()
    quotes_count = Quotation.objects.filter(customer=profile, status='sent').count()
    
    context = {
        'tickets_count': tickets_count,
        'quotes_count': quotes_count,
        'profile': profile
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def quotations_list(request):
    if not is_customer(request.user): return redirect('/admin/')
    profile = request.user.customerprofile
    # Only show quotes that are sent or accepted/rejected
    quotes = Quotation.objects.filter(customer=profile, status__in=['sent', 'accepted', 'rejected']).order_by('-created_at')
    
    return render(request, 'portal/quotations.html', {'quotes': quotes})

@login_required
def accept_quotation(request, quote_id):
    if not is_customer(request.user): return redirect('/admin/')
    if request.method == 'POST':
        profile = request.user.customerprofile
        quote = get_object_or_404(Quotation, id=quote_id, customer=profile, status='sent')
        quote.status = 'accepted'
        quote.save()
        first_item = quote.items.first()
        product_name = first_item.product.name if first_item and first_item.product else "your requested products"
        messages.success(request, f'Quotation for {product_name} has been accepted.')
    return redirect('quotations_list')

@login_required
def tickets_list(request):
    if not is_customer(request.user): return redirect('/admin/')
    profile = request.user.customerprofile
    tickets = ServiceTicket.objects.filter(customer=profile).order_by('-created_at')
    return render(request, 'portal/tickets.html', {'tickets': tickets})

@login_required
def create_ticket(request):
    if not is_customer(request.user): return redirect('/admin/')
    profile = request.user.customerprofile
    
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        priority = request.POST.get('priority')
        product_id = request.POST.get('product')
        division_id = request.POST.get('division')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        
        product = Product.objects.get(id=product_id) if product_id else None
        
        ticket = ServiceTicket.objects.create(
            company=profile.company,
            customer=profile,
            product=product,
            issue_title=title,
            description=desc,
            priority=priority
        )
        
        if division_id:
            try:
                ticket.division = Division.objects.get(id=division_id)
            except Division.DoesNotExist:
                pass
        if category_id:
            try:
                ticket.category = ProductCategory.objects.get(id=category_id)
            except ProductCategory.DoesNotExist:
                pass
        if subcategory_id:
            try:
                ticket.subcategory = ProductSubCategory.objects.get(id=subcategory_id)
            except ProductSubCategory.DoesNotExist:
                pass
        ticket.save()
        
        messages.success(request, 'Your service ticket has been submitted successfully.')
        return redirect('tickets_list')
        
    divisions = Division.objects.filter(company=profile.company)
    return render(request, 'portal/ticket_create.html', {'divisions': divisions})

# ==========================================
# ENGINEER PORTAL VIEWS
# ==========================================

@login_required
def engineer_dashboard(request):
    if not is_engineer(request.user): return redirect('/admin/')
    
    try:
        employee = request.user.employee
    except:
        return HttpResponseForbidden("Employee profile not found.")
        
    assigned_tickets = ServiceTicket.objects.filter(assigned_engineers=employee).exclude(status__in=['resolved', 'closed']).count()
    resolved_tickets = ServiceTicket.objects.filter(assigned_engineers=employee, status='resolved').count()
    
    context = {
        'employee': employee,
        'assigned_tickets': assigned_tickets,
        'resolved_tickets': resolved_tickets,
    }
    return render(request, 'engineer/dashboard.html', context)

@login_required
def engineer_tickets(request):
    if not is_engineer(request.user): return redirect('/admin/')
    employee = request.user.employee
    
    # Show active tickets first, then resolved/closed
    tickets = ServiceTicket.objects.filter(assigned_engineers=employee).order_by('status', '-created_at')
    return render(request, 'engineer/tickets.html', {'tickets': tickets})

@login_required
def engineer_ticket_update(request, ticket_id):
    if not is_engineer(request.user): return redirect('/admin/')
    employee = request.user.employee
    
    ticket = get_object_or_404(ServiceTicket, id=ticket_id, assigned_engineers=employee)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('resolution_notes')

        if new_status:
            ticket.status = new_status
        if notes:
            ticket.resolution_notes = notes

        try:
            ticket.full_clean()
            ticket.save()
            messages.success(request, f'Ticket #{ticket.id} has been updated successfully.')
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
        return redirect('engineer_tickets')
        
    return render(request, 'engineer/ticket_update.html', {'ticket': ticket})

# ==========================================
# PDF GENERATION VIEWS
# ==========================================
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO
from .models import Quotation, Invoice

@login_required
def generate_pdf_quotation(request, quote_id):
    # Admins or the specific customer can download
    quote = get_object_or_404(Quotation, id=quote_id)
    
    # Check permission
    if not (request.user.is_superuser or (is_customer(request.user) and quote.customer == request.user.customerprofile)):
        return HttpResponseForbidden("You do not have permission to download this quotation.")
        
    template = get_template('pdf/quotation_pdf.html')
    
    # Calculate discount amount
    subtotal = quote.get_subtotal()
    discount_amount = subtotal * (quote.admin_discount_percent / 100)
    
    context = {
        'quotation': quote,
        'discount_amount': discount_amount
    }
    
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"Quotation_{quote.quotation_number}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("Error generating PDF", status=400)

@login_required
def generate_pdf_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    template = get_template('pdf/invoice_pdf.html')
    context = {'invoice': invoice}
    
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename_num = invoice.invoice_number if invoice.invoice_number else invoice.id
        response['Content-Disposition'] = f'attachment; filename="Invoice_{filename_num}.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)

@login_required
def generate_pdf_stock_report(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this report.")

    from .models import Godown, StockItem

    godown_id = request.GET.get('godown')
    ids_param = request.GET.get('ids')
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    unit = request.GET.get('unit')
    low_stock_only = request.GET.get('low_stock_only') == '1'

    items = StockItem.objects.filter(is_active=True).select_related('category', 'subcategory')
    if ids_param:
        items = items.filter(pk__in=[i for i in ids_param.split(',') if i.isdigit()])
    if category_id:
        items = items.filter(category_id=category_id)
    if subcategory_id:
        items = items.filter(subcategory_id=subcategory_id)
    if unit:
        items = items.filter(unit=unit)

    godowns = Godown.objects.filter(is_active=True).order_by('godown_type', 'name')
    if godown_id:
        godowns = godowns.filter(pk=godown_id)

    summary_rows = []
    for item in items:
        total = item.get_stock_balance()
        low_stock = total <= item.reorder_level
        if low_stock_only and not low_stock:
            continue
        summary_rows.append({
            'item': item,
            'total': total,
            'low_stock': low_stock,
        })

    godown_sections = []
    for godown in godowns:
        rows = []
        for item in items:
            balance = item.get_stock_balance(godown=godown)
            if not balance:
                continue
            low_stock = balance <= item.reorder_level
            if low_stock_only and not low_stock:
                continue
            rows.append({'item': item, 'balance': balance, 'low_stock': low_stock})
        godown_sections.append({'godown': godown, 'rows': rows})

    template = get_template('pdf/stock_report_pdf.html')
    context = {
        'company': Company.objects.order_by('pk').first(),
        'generated_at': timezone.now(),
        'summary_rows': summary_rows,
        'godown_sections': godown_sections,
        'filtered_godown': godowns.first() if godown_id else None,
    }

    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="Current_Stock_Report.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)

@login_required
def stock_report_filters_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this report.")

    from .models import Godown, StockCategory, StockSubCategory, StockItem

    context = {
        'godowns': Godown.objects.filter(is_active=True).order_by('godown_type', 'name'),
        'categories': StockCategory.objects.filter(is_active=True).order_by('name'),
        'subcategories': StockSubCategory.objects.filter(is_active=True).select_related('category').order_by('category__name', 'name'),
        'units': StockItem.UNIT_CHOICES,
    }
    return render(request, 'admin/store/stock_report_filters.html', context)

# ==========================================
# PROJECT DEPARTMENT - PURCHASE REQUISITION
# ==========================================

@login_required
def stock_item_balance_api(request, item_id):
    from django.http import JsonResponse
    from .models import StockItem
    if not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)
    item = get_object_or_404(StockItem, pk=item_id)
    return JsonResponse({
        'balance': str(item.get_stock_balance()),
        'reorder_level': str(item.reorder_level),
        'unit': item.get_unit_display(),
    })

@login_required
def generate_pdf_purchase_requisition(request, pr_id):
    from .models import PurchaseRequisition
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this requisition.")

    pr = get_object_or_404(PurchaseRequisition, id=pr_id)
    template = get_template('pdf/purchase_requisition_pdf.html')
    context = {
        'company': pr.company,
        'pr': pr,
        'generated_at': timezone.now(),
    }

    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Purchase_Requisition_{pr.pr_number}.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)

@login_required
def email_purchase_requisition(request, pr_id):
    from django.core.mail import EmailMessage
    from .models import PurchaseRequisition

    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to email this requisition.")

    pr = get_object_or_404(PurchaseRequisition, id=pr_id)

    if request.method == 'POST':
        to_email = request.POST.get('email', '').strip()
        note = request.POST.get('note', '').strip()
        if not to_email:
            messages.error(request, 'Please enter an email address.')
            return redirect('email_purchase_requisition', pr_id=pr.id)

        template = get_template('pdf/purchase_requisition_pdf.html')
        context = {'company': pr.company, 'pr': pr, 'generated_at': timezone.now()}
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if pdf.err:
            messages.error(request, 'Could not generate the PDF for this requisition.')
            return redirect('email_purchase_requisition', pr_id=pr.id)

        subject = f'Purchase Requisition {pr.pr_number} - {pr.project.project_number}'
        body = note or f'Please find attached Purchase Requisition {pr.pr_number} for project {pr.project.project_number} ({pr.project.customer.business_name}).'
        email = EmailMessage(subject, body, to=[to_email])
        email.attach(f'Purchase_Requisition_{pr.pr_number}.pdf', result.getvalue(), 'application/pdf')
        try:
            email.send(fail_silently=False)
            messages.success(request, f'Requisition emailed to {to_email}.')
        except Exception as e:
            messages.error(request, f'Could not send email - check email server settings. ({e})')
        return redirect('admin:project_purchaserequisition_change', pr.id)

    return render(request, 'admin/project/email_purchase_requisition.html', {'pr': pr})

# ==========================================
# PURCHASE DEPARTMENT - SUPPLIER PURCHASE ORDER
# ==========================================

@login_required
def generate_pdf_supplier_po(request, po_id):
    from .models import SupplierPurchaseOrder
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this purchase order.")

    po = get_object_or_404(SupplierPurchaseOrder, id=po_id)
    template = get_template('pdf/supplier_po_pdf.html')
    context = {'company': po.company, 'po': po, 'generated_at': timezone.now()}

    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Purchase_Order_{po.po_number}.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)

@login_required
def email_supplier_po(request, po_id):
    from django.core.mail import EmailMessage
    from .models import SupplierPurchaseOrder

    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to email this purchase order.")

    po = get_object_or_404(SupplierPurchaseOrder, id=po_id)

    if request.method == 'POST':
        to_email = request.POST.get('email', '').strip() or po.supplier.email
        note = request.POST.get('note', '').strip()
        if not to_email:
            messages.error(request, 'Please enter an email address (this supplier has none on file).')
            return redirect('email_supplier_po', po_id=po.id)

        template = get_template('pdf/supplier_po_pdf.html')
        context = {'company': po.company, 'po': po, 'generated_at': timezone.now()}
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if pdf.err:
            messages.error(request, 'Could not generate the PDF for this purchase order.')
            return redirect('email_supplier_po', po_id=po.id)

        subject = f'Purchase Order {po.po_number} from {po.company.name}'
        body = note or f'Dear {po.supplier.name},\n\nPlease find attached Purchase Order {po.po_number}.\n\nRegards,\n{po.company.name}'
        email = EmailMessage(subject, body, to=[to_email])
        email.attach(f'Purchase_Order_{po.po_number}.pdf', result.getvalue(), 'application/pdf')
        try:
            email.send(fail_silently=False)
            if po.status == 'draft':
                po.status = 'sent'
                po.save()
            messages.success(request, f'Purchase Order emailed to {to_email}.')
        except Exception as e:
            messages.error(request, f'Could not send email - check email server settings. ({e})')
        return redirect('admin:purchase_supplierpurchaseorder_change', po.id)

    return render(request, 'admin/purchase/email_supplier_po.html', {'po': po})

@login_required
def whatsapp_share_supplier_po(request, po_id):
    from urllib.parse import quote
    from .models import SupplierPurchaseOrder

    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to share this purchase order.")

    po = get_object_or_404(SupplierPurchaseOrder, id=po_id)
    digits = ''.join(ch for ch in po.supplier.whatsapp_number if ch.isdigit())
    if not digits:
        messages.error(request, f"{po.supplier.name} has no WhatsApp number on file - add one in the Supplier record first.")
        return redirect('admin:purchase_supplierpurchaseorder_change', po.id)

    pdf_url = request.build_absolute_uri(reverse('generate_pdf_supplier_po', args=[po.id]))
    message = f"Purchase Order {po.po_number} from {po.company.name}. View/download: {pdf_url}"

    if po.status == 'draft':
        po.status = 'sent'
        po.save()

    return redirect(f"https://wa.me/{digits}?text={quote(message)}")

# ==========================================
# SERVICE HUB - EQUIPMENT REPORT
# ==========================================

@login_required
def generate_pdf_equipment_report(request):
    from .models import Equipment
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this report.")

    ids_param = request.GET.get('ids')
    equipment = Equipment.objects.select_related('customer', 'category', 'subcategory').order_by('customer__business_name')
    if ids_param:
        equipment = equipment.filter(pk__in=[i for i in ids_param.split(',') if i.isdigit()])

    template = get_template('pdf/equipment_report_pdf.html')
    context = {
        'company': Company.objects.order_by('pk').first(),
        'generated_at': timezone.now(),
        'equipment_list': equipment,
        'is_single': equipment.count() == 1,
    }

    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="Equipment_Report.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)

# ==========================================
# HR & ADMIN - LETTER GENERATION
# ==========================================

@login_required
def generate_pdf_hr_letter(request, employee_id, letter_type):
    from .models import Employee
    from django.http import Http404
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to generate this letter.")

    letter_titles = {
        'offer': 'Offer Letter',
        'experience': 'Experience Letter',
        'termination': 'Termination Letter',
    }
    if letter_type not in letter_titles:
        raise Http404("Unknown letter type.")

    employee = get_object_or_404(Employee, id=employee_id)
    template = get_template('pdf/hr_letter_pdf.html')
    context = {
        'company': employee.company,
        'employee': employee,
        'letter_type': letter_type,
        'letter_title': letter_titles[letter_type],
        'generated_at': timezone.now(),
    }

    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{letter_titles[letter_type].replace(" ", "_")}_{employee.employee_code}.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)
