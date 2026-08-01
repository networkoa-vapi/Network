from django.db import models
from core.models import ServiceTicket, AMCContract, Equipment, AMCCoverageItem

class ServiceServiceTicket(ServiceTicket):
    class Meta:
        proxy = True
        app_label = 'service'
        verbose_name = 'ServiceTicket'
        verbose_name_plural = 'Service Tickets'


class PendingComplaintsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(outcome='pending')

class PendingComplaints(ServiceTicket):
    """Every complaint currently marked Pending - carries over day to day until it's actioned and closed."""
    objects = PendingComplaintsManager()

    class Meta:
        proxy = True
        app_label = 'service'
        verbose_name = 'Pending Complaint'
        verbose_name_plural = 'Pending Complaints'

class ServiceAMCContract(AMCContract):
    class Meta:
        proxy = True
        app_label = 'service'
        verbose_name = 'AMCContract'
        verbose_name_plural = 'AMC Contracts'

class ServiceEquipment(Equipment):
    class Meta:
        proxy = True
        app_label = 'service'
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'

class ServiceAMCCoverageItem(AMCCoverageItem):
    class Meta:
        proxy = True
        app_label = 'service'
        verbose_name = 'AMC Coverage Item'
        verbose_name_plural = 'AMC Coverage Items'

