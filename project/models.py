from core.models import Project as CoreProject, PurchaseRequisition as CorePurchaseRequisition

class Project(CoreProject):
    class Meta:
        proxy = True
        app_label = 'project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

class PurchaseRequisition(CorePurchaseRequisition):
    class Meta:
        proxy = True
        app_label = 'project'
        verbose_name = 'Purchase Requisition'
        verbose_name_plural = 'Purchase Requisitions'
