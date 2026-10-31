/* Smart Recipe – gọi Recipe Engine (Python) qua /api/adjust và hiển thị kết quả */
(function () {
  const cfg = JSON.parse(document.getElementById('smart-config').textContent);
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const sliders = $$('.taste-slider');
  const subs = $$('.sub-select');
  let servings = 1;
  let last = cfg.initial;
  let timer = null;
  let seq = 0;

  const vnd = (n) => Math.round(n).toLocaleString('vi-VN') + 'đ';
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function state() {
    const s = {};
    sliders.forEach((el) => { s[el.dataset.key] = Number(el.value); });
    const sub = {};
    subs.forEach((el) => { if (el.value) sub[el.dataset.index] = el.value; });
    return {
      source: cfg.source, id: cfg.id, servings: servings, sliders: s, subs: sub,
      keep_volume: $('#keep-volume').checked,
    };
  }

  function updateSliderLabels() {
    sliders.forEach((el) => {
      const v = Number(el.value);
      const out = document.getElementById('val-' + el.dataset.key);
      out.textContent = (v > 0 ? '+' : '') + v + '%';
      out.classList.toggle('pos', v > 0);
      out.classList.toggle('neg', v < 0);
    });
  }

  function request() {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      const my = ++seq;
      $('#result-panel').classList.add('is-loading');
      try {
        const res = await fetch(cfg.endpoint, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(state()),
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        if (my === seq) { last = data; render(data); }
      } catch (e) {
        $('#r-messages').innerHTML = '<li class="warn">Không kết nối được Recipe Engine. Hãy kiểm tra server đang chạy.</li>';
      } finally {
        if (my === seq) $('#result-panel').classList.remove('is-loading');
      }
    }, 140);
  }

  function render(d) {
    $('#r-volume').textContent = d.volume_ml;
    $('#r-cps').textContent = vnd(d.cost_per_serving);
    $('#r-cost').textContent = vnd(d.cost);

    $('#r-table tbody').innerHTML = d.ingredients.map((i) => {
      let cls = '';
      let after = `${i.qty} ${i.unit}`;
      if (i.qty > i.original_qty) cls = 'delta-up';
      else if (i.qty < i.original_qty) cls = 'delta-down';
      const name = i.substituted_from
        ? `${esc(i.name)} <span class="tiny muted">(thay ${esc(i.substituted_from)})</span>` : esc(i.name);
      const scale = i.scale === 'sublinear' && d.servings > 1 ? ' <span class="tiny muted" title="Không nhân tuyến tính">*</span>' : '';
      return `<tr class="${i.changed ? 'changed' : ''}"><td>${name}${scale}</td>` +
        `<td class="num">${i.original_qty} ${esc(i.unit)}</td>` +
        `<td class="num"><span class="${cls}">${after}</span></td></tr>`;
    }).join('');

    const msgs = d.warnings.map((w) => `<li class="warn">⚠ ${esc(w)}</li>`)
      .concat(d.notes.map((n) => `<li class="note">• ${esc(n)}</li>`));
    $('#r-messages').innerHTML = msgs.join('');

    // Ví dụ thay đổi dưới từng slider
    sliders.forEach((el) => {
      const role = el.dataset.role;
      const ex = document.getElementById('ex-' + el.dataset.key);
      const ing = d.ingredients.find((i) => i.role === role && i.original_qty !== i.qty && !i.substituted_from);
      ex.textContent = Number(el.value) !== 0 && ing
        ? `Ví dụ: ${ing.name} ${ing.original_qty} ${ing.unit} → ${ing.qty} ${ing.unit}` : '';
    });

    // So sánh hồ sơ vị
    const labels = Object.assign({}, cfg.axes, { milk: { label: 'Creaminess' } });
    $('#r-taste').innerHTML = Object.keys(d.taste).map((k) => {
      const a = d.original_taste[k] || 0;
      const b = d.taste[k];
      const delta = b - a;
      const sign = delta > 0 ? '+' : '';
      return `<div class="compare-row"><span>${esc((labels[k] || {}).label || k)}</span>` +
        `<div class="compare-bars"><span class="b0" style="width:${a}%"></span><span class="b1" style="width:${b}%"></span></div>` +
        `<span class="num small ${delta > 0 ? 'delta-up' : delta < 0 ? 'delta-down' : 'muted'}">${b}${delta ? ' (' + sign + delta + ')' : ''}</span></div>`;
    }).join('');

    const br = $('#r-brewing');
    if (br && d.brewing && d.brewing.tea) {
      const b = d.brewing;
      let time = b.minutes >= 60 ? Math.round(b.minutes / 60) + ' giờ' : b.minutes < 1 ? Math.round(b.minutes * 60) + ' giây' : b.minutes + ' phút';
      let txt = `${b.tea}: ${b.leaf_g_adjusted} g lá / ${b.water_ml} ml nước · ${b.temp}°C · ${time}`;
      if (b.leaf_g_adjusted !== b.leaf_g) txt += ` (gốc ${b.leaf_g} g – giữ nguyên nhiệt độ và thời gian ủ)`;
      br.textContent = txt;
    }
  }

  // Sự kiện
  sliders.forEach((el) => el.addEventListener('input', () => { updateSliderLabels(); request(); }));
  subs.forEach((el) => el.addEventListener('change', () => {
    const note = document.getElementById('subnote-' + el.dataset.index);
    const opt = el.selectedOptions[0];
    if (note) {
      if (opt && opt.dataset.label) {
        const cls = { 'Best Match': 'best', 'Flavor Twist': 'twist', 'Budget Option': 'budget' }[opt.dataset.label] || 'budget';
        note.innerHTML = `<span class="sub-label ${cls}">${esc(opt.dataset.label)}</span> ${esc(opt.dataset.note)}`;
      } else note.innerHTML = '';
    }
    request();
  }));
  $('#keep-volume').addEventListener('change', request);
  $('#srv-minus').addEventListener('click', () => { servings = Math.max(1, servings - 1); $('#servings').textContent = servings; request(); });
  $('#srv-plus').addEventListener('click', () => { servings = Math.min(20, servings + 1); $('#servings').textContent = servings; request(); });
  $('#reset').addEventListener('click', () => {
    sliders.forEach((el) => { el.value = 0; });
    subs.forEach((el) => { el.value = ''; el.dispatchEvent(new Event('change')); });
    servings = 1; $('#servings').textContent = 1; $('#keep-volume').checked = true;
    updateSliderLabels(); request();
  });

  // Lưu phiên bản
  $('#save-btn').addEventListener('click', async () => {
    const status = $('#save-status');
    const body = Object.assign(state(), {
      note: $('#save-note').value, major: $('#save-major').checked, is_public: $('#save-public').checked,
    });
    status.textContent = 'Đang lưu…';
    try {
      const res = await fetch(cfg.saveEndpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      });
      if (res.status === 401) { window.location = cfg.loginUrl; return; }
      const data = await res.json();
      if (data.ok) status.innerHTML = `Đã lưu phiên bản <strong>${esc(data.label)}</strong>. <a href="${data.url}">Xem và so sánh →</a>`;
      else status.textContent = 'Chưa lưu được, vui lòng thử lại.';
    } catch (e) { status.textContent = 'Lỗi kết nối, vui lòng thử lại.'; }
  });

  // Recipe card để chia sẻ
  $('#share-btn').addEventListener('click', async () => {
    const lines = [`🍵 ${cfg.name} – phiên bản của tôi (${last.servings} ly)`]
      .concat(last.ingredients.map((i) => `• ${i.name}: ${i.qty} ${i.unit}`))
      .concat([`Cost/ly: ${vnd(last.cost_per_serving)}`, window.location.href]);
    const text = lines.join('\n');
    try {
      if (navigator.share) await navigator.share({ title: cfg.name, text });
      else { await navigator.clipboard.writeText(text); $('#save-status').textContent = 'Đã sao chép recipe card vào clipboard.'; }
    } catch (e) { /* người dùng hủy */ }
  });

  // Tab trên mobile
  $$('.smart-tabs button').forEach((b) => b.addEventListener('click', () => {
    $$('.smart-tabs button').forEach((x) => { x.classList.toggle('btn-primary', x === b); x.classList.toggle('btn-secondary', x !== b); });
    $$('.smart-col').forEach((c) => c.classList.toggle('active', c.dataset.col === b.dataset.col));
  }));

  updateSliderLabels();
  render(cfg.initial);
})();
