from core.models import Division, Product, ProductCategory, ProductSubCategory, ProductDocument

class InventoryDivision(Division):
    class Meta:
        proxy = True
        app_label = 'inventory'
        verbose_name = 'Division'
        verbose_name_plural = 'Divisions'

class InventoryProduct(Product):
    class Meta:
        proxy = True
        app_label = 'inventory'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

class InventoryProductCategory(ProductCategory):
    class Meta:
        proxy = True
        app_label = 'inventory'
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

class InventoryProductSubCategory(ProductSubCategory):
    class Meta:
        proxy = True
        app_label = 'inventory'
        verbose_name = 'Product Sub-Category'
        verbose_name_plural = 'Product Sub-Categories'

class InventoryProductDocument(ProductDocument):
    class Meta:
        proxy = True
        app_label = 'inventory'
        verbose_name = 'Product Document'
        verbose_name_plural = 'Product Documents'

