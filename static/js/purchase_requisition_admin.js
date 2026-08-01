/**
 * Purchase Requisition admin: as soon as a Stock Item is picked (and as the
 * Quantity is typed), shows current stock, shortfall, and the recommended
 * purchase quantity - which tops up to the item's Minimum Stock Level
 * (reorder level) on top of covering the shortfall, not just the bare gap.
 */
(function () {
    'use strict';

    function attachHandler(select) {
        if (select.dataset.stockLevelBound) return;
        select.dataset.stockLevelBound = '1';

        var row = select.closest('tr') || select.closest('.form-row');
        var qtyInput = row ? row.querySelector('input[id$="-quantity"]') : null;

        var hint = document.createElement('div');
        hint.className = 'stock-level-hint';
        hint.style.cssText = 'font-size:11px; color:#666; margin-top:4px;';
        select.insertAdjacentElement('afterend', hint);

        var cache = {};

        function render() {
            var data = cache[select.value];
            if (!data) {
                hint.textContent = '';
                return;
            }
            var balance = parseFloat(data.balance) || 0;
            var reorderLevel = parseFloat(data.reorder_level) || 0;
            var quantity = qtyInput ? (parseFloat(qtyInput.value) || 0) : 0;

            var text = 'Current stock: ' + data.balance + ' ' + data.unit;
            text += ' | MSL: ' + data.reorder_level + ' ' + data.unit;

            if (quantity > balance) {
                var shortfall = quantity - balance;
                var toPurchase = shortfall + reorderLevel;
                text += ' | Short by ' + shortfall.toFixed(2) + ' ' + data.unit;
                text += ' | Recommended purchase (incl. MSL): ' + toPurchase.toFixed(2) + ' ' + data.unit;
                hint.style.color = '#b45309';
            } else {
                hint.style.color = '#16a34a';
                text += ' | In stock for this requisition';
            }
            hint.textContent = text;
        }

        function update() {
            if (!select.value) {
                hint.textContent = '';
                return;
            }
            if (cache[select.value]) {
                render();
                return;
            }
            hint.textContent = 'Checking stock…';
            fetch('/store/stock-item/' + select.value + '/balance/')
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    cache[select.value] = data;
                    render();
                })
                .catch(function () { hint.textContent = ''; });
        }

        select.addEventListener('change', update);
        if (qtyInput) {
            qtyInput.addEventListener('input', render);
        }
        if (select.value) update();
    }

    function scan() {
        document.querySelectorAll('select[id$="-stock_item"]').forEach(attachHandler);
    }

    document.addEventListener('DOMContentLoaded', function () {
        scan();
        var observer = new MutationObserver(function () { scan(); });
        observer.observe(document.body, { childList: true, subtree: true });
    });
})();
