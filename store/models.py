from django.db import models
from core.models import Godown, StockCategory, StockSubCategory, StockItem, StockTransaction, PurchaseRequisitionItem

class StoreGodown(Godown):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Godown'
        verbose_name_plural = 'Godowns'

class StoreStockCategory(StockCategory):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Stock Category'
        verbose_name_plural = 'Stock Categories'

class StoreStockSubCategory(StockSubCategory):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Stock Sub-Category'
        verbose_name_plural = 'Stock Sub-Categories'

class StoreStockItem(StockItem):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Stock Item'
        verbose_name_plural = 'Stock Items'

class StoreStockTransaction(StockTransaction):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'


class PurchaseInwardManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='receipt')

class PurchaseInward(StockTransaction):
    """Dedicated 'Purchase Inward' tab: only Stock Receipt transactions."""
    objects = PurchaseInwardManager()

    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Purchase Inward'
        verbose_name_plural = 'Purchase Inward'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transaction_type = 'receipt'


class MaterialIssueManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='issue')

class MaterialIssue(StockTransaction):
    """Dedicated 'Issue' tab: only Issued-to-Party transactions (any category - goods, tools, capital items, etc.)."""
    objects = MaterialIssueManager()

    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Material Issue'
        verbose_name_plural = 'Material Issue'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transaction_type = 'issue'


class ItemsToIssue(PurchaseRequisitionItem):
    """Store Department: Purchase Requisition lines covered by current stock, ready to issue."""
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Item to Issue'
        verbose_name_plural = 'Items to Issue'
