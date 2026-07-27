from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_login, name='portal_login'),
    path('logout/', views.portal_logout, name='portal_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quotations/', views.quotations_list, name='quotations_list'),
    path('quotations/<int:quote_id>/accept/', views.accept_quotation, name='accept_quotation'),
    path('tickets/', views.tickets_list, name='tickets_list'),
    path('tickets/new/', views.create_ticket, name='create_ticket'),
    
    # Engineer Portal Routes
    path('engineer/', views.engineer_dashboard, name='engineer_dashboard'),
    path('engineer/tickets/', views.engineer_tickets, name='engineer_tickets'),
    path('engineer/ticket/<int:ticket_id>/', views.engineer_ticket_update, name='engineer_ticket_update'),
    
    # PDF Generation
    path('quotation/<int:quote_id>/pdf/', views.generate_pdf_quotation, name='generate_pdf_quotation'),
    path('invoice/<int:invoice_id>/pdf/', views.generate_pdf_invoice, name='generate_pdf_invoice'),
]
