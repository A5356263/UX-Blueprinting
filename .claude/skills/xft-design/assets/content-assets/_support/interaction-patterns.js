/* XFT Interaction Patterns — 可交互原型的标准 JS 片段
   使用方式：在页面 <script> 中 shell runtime 之后追加需要的 pattern
   所有 pattern 通过 data-action 属性绑定，不依赖特定 class */

/* ── Pattern 1: 表格行选择 → 批量按钮联动 ── */
(function() {
  var table = document.querySelector('.data-table');
  if (!table) return;
  var checkAll = table.querySelector('thead input[type="checkbox"]');
  var rowChecks = table.querySelectorAll('tbody input[type="checkbox"]');
  var selBar = document.querySelector('.sel-bar');
  var batchBtns = document.querySelectorAll('[data-action="batch"]');
  var selCount = selBar ? selBar.querySelector('strong') : null;
  var selAmount = selBar ? selBar.querySelectorAll('strong')[1] : null;

  function updateBatch() {
    var checked = table.querySelectorAll('tbody input[type="checkbox"]:checked');
    var count = checked.length;
    if (selBar) selBar.style.display = count > 0 ? 'flex' : 'none';
    if (selCount) selCount.textContent = count;
    // Sum amounts (look for amount in the row)
    var total = 0;
    checked.forEach(function(cb) {
      var row = cb.closest('tr');
      if (!row) return;
      var cells = row.querySelectorAll('td');
      // Find cell with ¥ in the 4th or 5th column (common patterns)
      cells.forEach(function(cell) {
        var t = cell.textContent.replace(/[^0-9.]/g, '');
        if (t && cell.style.fontWeight === 'var(--fw-bold)') total += parseFloat(t) || 0;
      });
    });
    if (selAmount) selAmount.textContent = '¥' + total.toLocaleString('zh-CN', {minimumFractionDigits: 2});
    // Toggle batch buttons
    batchBtns.forEach(function(btn) { btn.disabled = count === 0; });
  }

  if (checkAll) {
    checkAll.addEventListener('change', function() {
      rowChecks.forEach(function(cb) { cb.checked = checkAll.checked; });
      updateBatch();
    });
  }
  rowChecks.forEach(function(cb) {
    cb.addEventListener('change', updateBatch);
  });
  // Init: hide selBar if no selection
  if (selBar) selBar.style.display = 'none';
})();

/* ── Pattern 2: 审批操作 → 确认弹窗 → 状态更新 ── */
(function() {
  // Approve/Reject buttons in confirm modal
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-action="confirm-approve"]');
    if (btn) {
      // Close overlay
      var overlay = btn.closest('.xft-overlay-root');
      if (overlay) overlay.classList.remove('is-open');
      // Update status tag
      var statusTag = document.querySelector('.approval-info .tag-warn, .meta-list .tag-warn');
      if (statusTag) {
        statusTag.textContent = '已通过';
        statusTag.classList.remove('tag-warn');
        statusTag.classList.add('tag-ok');
      }
      // Move approval flow to next node
      var curNode = document.querySelector('.flow-node.cur');
      if (curNode) {
        curNode.classList.remove('cur');
        curNode.classList.add('done');
        // Update the node title tag
        var tag = curNode.querySelector('.tag-warn');
        if (tag) { tag.textContent = '已通过'; tag.classList.remove('tag-warn'); tag.classList.add('tag-ok'); }
        // Activate next pending node
        var nextNode = curNode.nextElementSibling;
        if (nextNode && nextNode.classList.contains('flow-node') && nextNode.classList.contains('pending')) {
          nextNode.classList.remove('pending');
          nextNode.classList.add('cur');
        }
      }
      // Update action bar: remove approve/reject, show export/print
      var actionBar = document.querySelector('.action-buttons');
      if (actionBar) {
        var primary = actionBar.querySelector('.btn-primary');
        var danger = actionBar.querySelector('.btn-danger');
        if (primary && primary.textContent.includes('审批') || primary && primary.textContent.includes('同意')) primary.style.display = 'none';
        if (danger) danger.style.display = 'none';
      }
    }

    var rejectBtn = e.target.closest('[data-action="confirm-reject"]');
    if (rejectBtn) {
      var overlay = rejectBtn.closest('.xft-overlay-root');
      if (overlay) overlay.classList.remove('is-open');
      var statusTag = document.querySelector('.approval-info .tag-warn, .meta-list .tag-warn');
      if (statusTag) {
        statusTag.textContent = '已驳回';
        statusTag.classList.remove('tag-warn');
        statusTag.classList.add('tag-err');
      }
      var curNode = document.querySelector('.flow-node.cur');
      if (curNode) {
        curNode.classList.remove('cur');
        var tag = curNode.querySelector('.tag-warn');
        if (tag) { tag.textContent = '已驳回'; tag.classList.remove('tag-warn'); tag.classList.add('tag-err'); }
      }
    }
  });
})();

/* ── Pattern 3: 删除/危险操作 → 确认弹窗 → 移除行 ── */
(function() {
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-action="confirm-delete"]');
    if (btn) {
      var overlay = btn.closest('.xft-overlay-root');
      if (overlay) overlay.classList.remove('is-open');
      // Remove target row (stored in overlay data attribute)
      var targetId = overlay.getAttribute('data-target-row');
      if (targetId) {
        var row = document.getElementById(targetId);
        if (row) row.remove();
      }
    }
  });
})();
