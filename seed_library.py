import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noa_erp.settings')
django.setup()

from core.models import Company, ProductCategory, ProductDocument
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from io import BytesIO

def create_dummy_pdf(title, text):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, title)
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, text)
    p.drawString(100, 680, "This is a placeholder for the actual Blue Star PDF.")
    p.save()
    buffer.seek(0)
    return buffer.read()

def run():
    company = Company.objects.first()
    
    # Try to find the RAC category
    try:
        rac_cat = ProductCategory.objects.get(name__icontains='Room Air Conditioners')
    except ProductCategory.DoesNotExist:
        print("RAC Category not found. Exiting.")
        return
        
    print("Generating sample RAC Brochure...")
    pdf_content = create_dummy_pdf("Blue Star Room AC Brochure 2024", "Explore our range of Inverter, Fixed Speed, and Window ACs.")
    
    doc, created = ProductDocument.objects.get_or_create(
        company=company,
        category=rac_cat,
        title="2024 Room AC Brochure",
        document_type="brochure"
    )
    if not doc.file:
        doc.file.save("BlueStar_RAC_Brochure_2024.pdf", ContentFile(pdf_content))
    doc.save()
    print("RAC Brochure Seeded!")

    # Try to find the CREF category
    try:
        cref_cat = ProductCategory.objects.get(name__icontains='Commercial Refrigeration')
        
        print("Generating sample CREF Brochure...")
        pdf_content2 = create_dummy_pdf("Blue Star Deep Freezers & Coolers 2024", "Explore our range of Hard Top, Glass Top Freezers and Water Coolers.")
        
        doc2, created2 = ProductDocument.objects.get_or_create(
            company=company,
            category=cref_cat,
            title="2024 Deep Freezers & Coolers Brochure",
            document_type="brochure"
        )
        if not doc2.file:
            doc2.file.save("BlueStar_CREF_Brochure_2024.pdf", ContentFile(pdf_content2))
        doc2.save()
        print("CREF Brochure Seeded!")
    except ProductCategory.DoesNotExist:
        pass

if __name__ == '__main__':
    run()
