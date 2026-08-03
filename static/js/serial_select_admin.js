/**
 * Store admin: keeps the "Serial Numbers" multi-select and the Purchase Inward "new
 * serial numbers" / "new pieces" textareas in sync with whichever Stock Item is currently
 * selected on the same form - e.g. picking the "Split AC - IDU" item narrows the serial
 * list down to only that item's available IDU units.
 */
(function () {
    'use strict';

    function getRow(el) {
        return el.closest('.form-row') || el.closest('tr');
    }

    function setRowVisible(el, visible) {
        var row = getRow(el);
        if (row) row.style.display = visible ? '' : 'none';
    }

    function findStockItemSelect(form) {
        return form ? (form.querySelector('select#id_stock_item') || form.querySelector('select[id$="-stock_item"]')) : null;
    }

    function populateSerials(select, itemId, statuses) {
        if (!itemId) {
            select.innerHTML = '';
            return;
        }
        fetch('/store/stock-item/' + itemId + '/serials/?statuses=' + encodeURIComponent(statuses))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var selected = Array.prototype.map.call(select.selectedOptions, function (o) { return o.value; });
                select.innerHTML = '';
                data.forEach(function (s) {
                    var opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = s.serial_number + (s.status !== 'in_stock' ? ' (' + s.status + ')' : '');
                    if (selected.indexOf(String(s.id)) !== -1) opt.selected = true;
                    select.appendChild(opt);
                });
            })
            .catch(function () { select.innerHTML = ''; });
    }

    function attachSerialsHandler(select) {
        if (select.dataset.serialsBound) return;
        select.dataset.serialsBound = '1';

        var statuses = select.dataset.statuses || 'in_stock';
        var stockItemSelect = findStockItemSelect(select.closest('form'));
        if (!stockItemSelect) return;

        // Only re-filter on an actual change - the page's initial render already
        // has the correct options (including any already-linked serials).
        stockItemSelect.addEventListener('change', function () {
            populateSerials(select, stockItemSelect.value, statuses);
        });
    }

    function attachNewSerialTextareaHandler(textarea) {
        if (textarea.dataset.serialsBound) return;
        textarea.dataset.serialsBound = '1';

        var stockItemSelect = findStockItemSelect(textarea.closest('form'));
        if (!stockItemSelect) return;

        function update() {
            if (!stockItemSelect.value) {
                setRowVisible(textarea, false);
                return;
            }
            fetch('/store/stock-item/' + stockItemSelect.value + '/balance/')
                .then(function (r) { return r.json(); })
                .then(function (data) { setRowVisible(textarea, !!data.is_serialized); })
                .catch(function () {});
        }

        stockItemSelect.addEventListener('change', update);
        if (stockItemSelect.value) update();
    }

    function populatePieces(select, itemId, statuses) {
        if (!itemId) {
            select.innerHTML = '';
            return;
        }
        fetch('/store/stock-item/' + itemId + '/pieces/?statuses=' + encodeURIComponent(statuses))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var selected = Array.prototype.map.call(select.selectedOptions, function (o) { return o.value; });
                select.innerHTML = '';
                data.forEach(function (p) {
                    var opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.label + ' - ' + p.quantity + (p.status !== 'in_stock' ? ' (' + p.status + ')' : '');
                    if (selected.indexOf(String(p.id)) !== -1) opt.selected = true;
                    select.appendChild(opt);
                });
            })
            .catch(function () { select.innerHTML = ''; });
    }

    function attachPiecesHandler(select) {
        if (select.dataset.piecesBound) return;
        select.dataset.piecesBound = '1';

        var statuses = select.dataset.pieceStatuses || 'in_stock';
        var stockItemSelect = findStockItemSelect(select.closest('form'));
        if (!stockItemSelect) return;

        stockItemSelect.addEventListener('change', function () {
            populatePieces(select, stockItemSelect.value, statuses);
        });
    }

    function attachNewPiecesTextareaHandler(textarea) {
        if (textarea.dataset.piecesBound) return;
        textarea.dataset.piecesBound = '1';

        var stockItemSelect = findStockItemSelect(textarea.closest('form'));
        if (!stockItemSelect) return;

        function update() {
            if (!stockItemSelect.value) {
                setRowVisible(textarea, false);
                return;
            }
            fetch('/store/stock-item/' + stockItemSelect.value + '/balance/')
                .then(function (r) { return r.json(); })
                .then(function (data) { setRowVisible(textarea, !!data.is_piece_tracked); })
                .catch(function () {});
        }

        stockItemSelect.addEventListener('change', update);
        if (stockItemSelect.value) update();
    }

    function scan() {
        document.querySelectorAll('select[data-statuses]').forEach(attachSerialsHandler);
        document.querySelectorAll('#id_new_serial_numbers').forEach(attachNewSerialTextareaHandler);
        document.querySelectorAll('select[data-piece-statuses]').forEach(attachPiecesHandler);
        document.querySelectorAll('#id_new_pieces').forEach(attachNewPiecesTextareaHandler);
    }

    document.addEventListener('DOMContentLoaded', function () {
        scan();
        var observer = new MutationObserver(function () { scan(); });
        observer.observe(document.body, { childList: true, subtree: true });
    });
})();
