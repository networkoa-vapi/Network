from django.db import models
from core.models import Godown, StockCategory, StockSubCategory, StockItem, StockItemSerial, StockItemPiece, StockTransaction, RefillLog, PurchaseRequisitionItem

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

class StoreStockItemSerial(StockItemSerial):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Stock Item Serial'
        verbose_name_plural = 'Stock Item Serials'

class StoreStockItemPiece(StockItemPiece):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Stock Item Piece'
        verbose_name_plural = 'Stock Item Pieces'

class RefillEntry(RefillLog):
    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Refill Entry'
        verbose_name_plural = 'Refill Entries'

class PendingReturnableItemsManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(
            transaction_type='issue', stock_item__is_returnable=True
        ).select_related('stock_item')
        pending_ids = [t.id for t in qs if t.is_pending_return]
        return super().get_queryset().filter(pk__in=pending_ids)

class PendingReturnableItems(StockTransaction):
    """Store Department report: returnable items (e.g. Tools) issued but not yet returned."""
    objects = PendingReturnableItemsManager()

    class Meta:
        proxy = True
        app_label = 'store'
        verbose_name = 'Pending Returnable Item'
        verbose_name_plural = 'Pending Returnable Items'


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
