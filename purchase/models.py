from core.models import PurchaseRequisitionItem, SupplierPurchaseOrder as CoreSupplierPurchaseOrder

class ItemsToPurchase(PurchaseRequisitionItem):
    """Purchase Department: Purchase Requisition lines short on stock - need external procurement."""
    class Meta:
        proxy = True
        app_label = 'purchase'
        verbose_name = 'Item to Purchase'
        verbose_name_plural = 'Items to Purchase'

class SupplierPurchaseOrder(CoreSupplierPurchaseOrder):
    class Meta:
        proxy = True
        app_label = 'purchase'
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
