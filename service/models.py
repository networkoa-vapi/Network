from core.models import ServiceTicket, AMCContract

class ServiceServiceTicket(ServiceTicket):
    class Meta:
        proxy = True
        app_label = 'service'
        verbose_name = 'ServiceTicket'
        verbose_name_plural = 'Service Tickets'

class ServiceAMCContract(AMCContract):
    class Meta:
        proxy = True
        app_label = 'service'
        verbose_name = 'AMCContract'
        verbose_name_plural = 'AMC Contracts'

