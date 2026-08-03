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
    path('store/stock-report/pdf/', views.generate_pdf_stock_report, name='generate_pdf_stock_report'),
    path('store/stock-report/filters/', views.stock_report_filters_view, name='stock_report_filters'),
    path('store/stock-item/<int:item_id>/balance/', views.stock_item_balance_api, name='stock_item_balance_api'),
    path('store/stock-item/<int:item_id>/serials/', views.stock_item_serials_api, name='stock_item_serials_api'),
    path('store/stock-item/<int:item_id>/pieces/', views.stock_item_pieces_api, name='stock_item_pieces_api'),
    path('project/pr/<int:pr_id>/pdf/', views.generate_pdf_purchase_requisition, name='generate_pdf_purchase_requisition'),
    path('project/pr/<int:pr_id>/email/', views.email_purchase_requisition, name='email_purchase_requisition'),
    path('purchase/po/<int:po_id>/pdf/', views.generate_pdf_supplier_po, name='generate_pdf_supplier_po'),
    path('purchase/po/<int:po_id>/email/', views.email_supplier_po, name='email_supplier_po'),
    path('purchase/po/<int:po_id>/whatsapp/', views.whatsapp_share_supplier_po, name='whatsapp_share_supplier_po'),
    path('service/equipment-report/pdf/', views.generate_pdf_equipment_report, name='generate_pdf_equipment_report'),
    path('hr/employee/<int:employee_id>/letter/<str:letter_type>/pdf/', views.generate_pdf_hr_letter, name='generate_pdf_hr_letter'),
    path('hr/offer-letter/<int:offer_id>/pdf/', views.generate_pdf_offer_letter, name='generate_pdf_offer_letter'),
    path('hr/offer-letter/<int:offer_id>/email/', views.email_offer_letter, name='email_offer_letter'),
    path('hr/offer-letter/<int:offer_id>/whatsapp/', views.whatsapp_share_offer_letter, name='whatsapp_share_offer_letter'),

    # Universal Reports Center
    path('reports/', views.reports_center, name='reports_center'),
    path('reports/download/', views.reports_download, name='reports_download'),
    path('reports/email/', views.reports_email, name='reports_email'),
    path('reports/whatsapp/', views.reports_whatsapp, name='reports_whatsapp'),
]
