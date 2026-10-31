/* Recipe Studio – thêm/xóa nguyên liệu, ước tính chi phí và thể tích */
(function () {
  const catalog = JSON.parse(document.getElementById('catalog-data').textContent);
  const body = document.getElementById('ing-body');
  const tpl = document.getElementById('ing-template');
  const servingsInput = document.getElementById('servings');

  const roleGuess = (name) => {
    const n = name.toLowerCase();
    if (n.startsWith('trà') || n.includes('matcha') || n.includes('hojicha') || n.includes('hibiscus')) return 'tea';
    if (n.includes('syrup đường') || n.includes('mật ong') || n.includes('vanilla') || n.includes('caramel')) return 'sweetener';
    if (n.includes('chanh') || n.includes('tắc') || n.includes('cam')) return 'acid';
    if (n.includes('sữa') || n.includes('foam')) return 'milk';
    if (n.includes('nước')) return 'water';
    if (n === 'đá') return 'ice';
    if (n.includes('syrup') || n.includes('đào') || n.includes('vải') || n.includes('xoài') || n.includes('dâu')) return 'fruit';
    return 'herb';
  };

  function recalc() {
    let cost = 0; let vol = 0;
    body.querySelectorAll('.ing-row').forEach((row) => {
      const name = row.querySelector('[name=ing_name]').value.trim();
      const qty = parseFloat(row.querySelector('[name=ing_qty]').value) || 0;
      const unit = row.querySelector('[name=ing_unit]').value;
      const role = row.querySelector('[name=ing_role]').value;
      const item = catalog[name];
      if (item) cost += qty * item.price;
      if (unit === 'ml' && role !== 'ice') vol += qty;
    });
    const s = Math.max(1, parseInt(servingsInput.value, 10) || 1);
    document.getElementById('est-cost').textContent = Math.round(cost / s).toLocaleString('vi-VN') + 'đ';
    document.getElementById('est-vol').textContent = Math.round(vol / s);
  }

  function wire(row) {
    const name = row.querySelector('[name=ing_name]');
    name.addEventListener('change', () => {
      const item = catalog[name.value.trim()];
      if (item) {
        row.querySelector('[name=ing_unit]').value = item.unit;
        row.querySelector('[name=ing_role]').value = roleGuess(name.value.trim());
      }
      recalc();
    });
    row.querySelectorAll('input, select').forEach((el) => el.addEventListener('input', recalc));
    row.querySelector('.ing-del').addEventListener('click', () => {
      if (body.querySelectorAll('.ing-row').length > 1) row.remove();
      else row.querySelectorAll('input').forEach((i) => { i.value = ''; });
      recalc();
    });
  }

  body.querySelectorAll('.ing-row').forEach(wire);
  document.getElementById('ing-add').addEventListener('click', () => {
    const row = tpl.content.firstElementChild.cloneNode(true);
    body.appendChild(row);
    wire(row);
    row.querySelector('[name=ing_name]').focus();
  });
  servingsInput.addEventListener('input', recalc);

  document.querySelectorAll('.taste-range').forEach((r) => {
    const out = document.querySelector(`[data-for="${r.id}"]`);
    r.addEventListener('input', () => { out.textContent = r.value; });
  });

  recalc();
})();
