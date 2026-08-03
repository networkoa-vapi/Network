from core.models import Employee, OfferLetter

class HREmployee(Employee):
    class Meta:
        proxy = True
        app_label = 'hr'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employee Master'

class HROfferLetter(OfferLetter):
    class Meta:
        proxy = True
        app_label = 'hr'
        verbose_name = 'Offer Letter'
        verbose_name_plural = 'Offer Letters'
