from django.contrib import admin
from .models import HREmployee
from core.admin import EmployeeAdmin

admin.site.register(HREmployee, EmployeeAdmin)
