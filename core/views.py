from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
        
    assigned_tickets = ServiceTicket.objects.filter(assigned_engineer=employee).exclude(status__in=['resolved', 'closed']).count()
    resolved_tickets = ServiceTicket.objects.filter(assigned_engineer=employee, status='resolved').count()
    
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
    tickets = ServiceTicket.objects.filter(assigned_engineer=employee).order_by('status', '-created_at')
    return render(request, 'engineer/tickets.html', {'tickets': tickets})

@login_required
def engineer_ticket_update(request, ticket_id):
    if not is_engineer(request.user): return redirect('/admin/')
    employee = request.user.employee
    
    ticket = get_object_or_404(ServiceTicket, id=ticket_id, assigned_engineer=employee)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('resolution_notes')
        
        if new_status:
            ticket.status = new_status
        if notes:
            ticket.resolution_notes = notes
            
        ticket.save()
        messages.success(request, f'Ticket #{ticket.id} has been updated successfully.')
        return redirect('engineer_tickets')
        
    return render(request, 'engineer/ticket_update.html', {'ticket': ticket})

# ==========================================
# PDF GENERATION VIEWS
# ==========================================
from django.template.loader import get_template
from django.http import HttpResponse
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
