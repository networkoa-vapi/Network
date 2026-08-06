from django import forms
from django.contrib import admin
from core.models import StockItemSerial, StockItemPiece
from .models import (
    StoreGodown, StoreStockCategory, StoreStockSubCategory, StoreStockItem, StoreStockTransaction,
    StoreStockItemSerial, StoreStockItemPiece, PurchaseInward, MaterialIssue, RefillEntry, PendingReturnableItems, ItemsToIssue,
)
from core.admin import (
    GodownAdmin, StockCategoryAdmin, StockSubCategoryAdmin, StockItemAdmin, StockTransactionAdmin,
    StockItemSerialAdmin, StockItemPieceAdmin, RefillLogAdmin, PendingReturnableItemsAdmin, ItemsToIssueAdmin,
    SerialSelectMediaMixin,
    # Unfold-styled base - importing import_export's own class here instead would
    # leave these two screens as unthemed stock Django admin pages.
    ImportExportModelAdmin,
)

admin.site.register(StoreGodown, GodownAdmin)
admin.site.register(StoreStockCategory, StockCategoryAdmin)
admin.site.register(StoreStockSubCategory, StockSubCategoryAdmin)
admin.site.register(StoreStockItem, StockItemAdmin)
admin.site.register(StoreStockTransaction, StockTransactionAdmin)
admin.site.register(StoreStockItemSerial, StockItemSerialAdmin)
admin.site.register(StoreStockItemPiece, StockItemPieceAdmin)


class PurchaseInwardForm(forms.ModelForm):
    new_serial_numbers = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'One serial number per line - only for serialized items'}),
        help_text="For serialized items only: enter each unit's serial number, one per line. Quantity is set automatically to match."
    )
    new_pieces = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'One piece size per line, e.g.\n30\n45\n25 - only for piece-tracked items'}),
        help_text="For piece-tracked items only: enter each piece's size (in the base Stock Unit), one per line. Quantity is set automatically to their total."
    )

    class Meta:
        model = PurchaseInward
        fields = '__all__'
        labels = {
            'transaction_uom': 'Purchase Unit',
            'transaction_uom_quantity': 'Quantity (Purchase Unit)',
            'expected_issue_uom': 'Issue Unit',
            'quantity': 'Quantity (Issue Unit)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For serialized/piece-tracked items, Quantity is derived from the entered
        # serials/pieces after save - default it to 0 so it never blocks submission.
        if not self.instance.pk:
            self.fields['quantity'].initial = 0


class PurchaseInwardAdmin(SerialSelectMediaMixin, ImportExportModelAdmin):
    form = PurchaseInwardForm
    list_display = ('voucher_number', 'stock_item', 'godown', 'quantity', 'transaction_date', 'handled_by', 'company')
    list_filter = ('company', 'godown', 'transaction_date')
    search_fields = ('voucher_number', 'stock_item__name', 'stock_item__item_code')
    readonly_fields = ('voucher_number',)
    fieldsets = (
        ('Purchase / Inward Details', {
            'fields': ('company', 'voucher_number', 'stock_item', 'godown'),
            'description': "Record material received into a Godown (from a purchase, or any other inward stock)."
        }),
        ('Purchase Unit & Quantity', {
            'fields': ('transaction_uom', 'transaction_uom_quantity', 'new_serial_numbers', 'new_pieces'),
            'description': "Reference only - what was actually purchased (e.g. 3 Kg of Copper Pipe). Doesn't affect the stock ledger."
        }),
        ('Issue Unit & Quantity', {
            'fields': ('expected_issue_uom', 'quantity'),
            'description': "What this becomes in the unit it's tracked/issued in (e.g. those 3 Kg measure out to 50 Ft) - enter the real quantity directly. This is the actual amount added to stock."
        }),
        ('Notes', {
            'fields': ('handled_by', 'remarks')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        serial_text = form.cleaned_data.get('new_serial_numbers', '').strip()
        if serial_text and obj.stock_item.is_serialized:
            numbers = [s.strip() for s in serial_text.splitlines() if s.strip()]
            created = [
                StockItemSerial.objects.get_or_create(stock_item=obj.stock_item, serial_number=num)[0]
                for num in numbers
            ]
            obj.serials.set(created)
            obj.sync_serial_statuses()

        pieces_text = form.cleaned_data.get('new_pieces', '').strip()
        if pieces_text and obj.stock_item.is_piece_tracked:
            sizes = []
            for line in pieces_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    sizes.append(float(line))
                except ValueError:
                    continue
            created = [StockItemPiece.objects.create(stock_item=obj.stock_item, quantity=size) for size in sizes]
            obj.pieces.set(created)
            obj.sync_piece_statuses()

admin.site.register(PurchaseInward, PurchaseInwardAdmin)


class MaterialIssueForm(forms.ModelForm):
    class Meta:
        model = MaterialIssue
        fields = '__all__'
        labels = {
            'transaction_uom': 'Alternate Unit',
            'transaction_uom_quantity': 'Quantity (Alternate Unit)',
            'quantity': 'Quantity (Stock Unit)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For serialized/piece-tracked items, Quantity is derived from the picked
        # serials/pieces after save - default it to 0 so it never blocks submission
        # before that selection is made.
        if not self.instance.pk:
            self.fields['quantity'].initial = 0


class MaterialIssueAdmin(SerialSelectMediaMixin, ImportExportModelAdmin):
    form = MaterialIssueForm
    list_display = ('voucher_number', 'stock_item', 'godown', 'quantity', 'sales_order', 'party_type', 'transaction_date', 'company')
    list_filter = ('company', 'godown', 'sales_order', 'party_type', 'transaction_date')
    search_fields = ('voucher_number', 'stock_item__name', 'stock_item__item_code', 'party_name')
    readonly_fields = ('voucher_number',)
    fieldsets = (
        ('Issue Details', {
            'fields': ('company', 'voucher_number', 'stock_item', 'godown'),
            'description': "Issue any stock item - Sales Goods, Tools, Capital Goods, Spare Parts, etc. - out of a Godown."
        }),
        ('Quantity', {
            'fields': ('quantity', 'serials', 'pieces'),
            'description': "The actual quantity issued, in the item's base Stock Unit. For serialized items, pick the specific unit(s) below - the list updates to show only that item's available serials. For piece-tracked items, pick one or more available pieces below - the list shows only that item's available pieces with their sizes."
        }),
        ('Alternate Unit (Reference Only)', {
            'fields': ('transaction_uom', 'transaction_uom_quantity'),
            'description': "Optional: also record this issue in a different unit for reference (e.g. the customer's PO says Metres). Doesn't affect Quantity (Stock Unit) above."
        }),
        ('Project', {
            'fields': ('sales_order',),
            'description': "Link to the customer project this material is issued for, so it can be tracked and billed back to the party."
        }),
        ('Issued To', {
            'fields': ('party_type', 'issued_to_employee', 'issued_to_customer', 'party_name')
        }),
        ('Notes', {
            'fields': ('handled_by', 'remarks')
        }),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        object_id = request.resolver_match.kwargs.get('object_id') if request.resolver_match else None
        if db_field.name == 'serials':
            qs = StockItemSerial.objects.filter(status='in_stock')
            if object_id:
                qs = qs | StockItemSerial.objects.filter(transactions__pk=object_id)
            kwargs['queryset'] = qs.distinct().select_related('stock_item')
            kwargs['widget'] = forms.SelectMultiple(attrs={'data-statuses': 'in_stock', 'size': 8})
        if db_field.name == 'pieces':
            qs = StockItemPiece.objects.filter(status='in_stock')
            if object_id:
                qs = qs | StockItemPiece.objects.filter(transactions__pk=object_id)
            kwargs['queryset'] = qs.distinct().select_related('stock_item')
            kwargs['widget'] = forms.SelectMultiple(attrs={'data-piece-statuses': 'in_stock', 'size': 8})
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.sync_serial_statuses()
        form.instance.sync_piece_statuses()

admin.site.register(MaterialIssue, MaterialIssueAdmin)

admin.site.register(RefillEntry, RefillLogAdmin)
admin.site.register(PendingReturnableItems, PendingReturnableItemsAdmin)
admin.site.register(ItemsToIssue, ItemsToIssueAdmin)
