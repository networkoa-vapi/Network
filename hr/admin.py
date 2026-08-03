from django.contrib import admin
from .models import HREmployee, HROfferLetter
from core.admin import EmployeeAdmin, OfferLetterAdmin

admin.site.register(HREmployee, EmployeeAdmin)
admin.site.register(HROfferLetter, OfferLetterAdmin)
