from core.models import Employee

class HREmployee(Employee):
    class Meta:
        proxy = True
        app_label = 'hr'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employee Master'
