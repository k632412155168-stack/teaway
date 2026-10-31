/* Tea Garden – game 2D nhẹ chạy trên web (vanilla JS)
   Vòng lặp: Plant → Care → Harvest → Process → Blend → Brew/Serve → Collect */
(function () {
  const root = document.getElementById('game');
  const AUTH = root.dataset.auth === '1';
  const API = root.dataset.api;
  const RECIPE_LINKS = JSON.parse(document.getElementById('game-recipes').textContent);
  const KEY = 'teaway_garden_v1';
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // ---------------------------- Dữ liệu game ----------------------------
  const LEVELS = [
    { lvl: 1, xp: 0, title: 'Tea Seedling', plots: 4 },
    { lvl: 2, xp: 50, title: 'Leaf Keeper', plots: 6 },
    { lvl: 3, xp: 130, title: 'Tea Artisan', plots: 8 },
    { lvl: 4, xp: 240, title: 'Flavor Alchemist', plots: 9 },
    { lvl: 5, xp: 380, title: 'Tea House Master', plots: 12 },
  ];
  const CROPS = {
    green:   { name: 'Trà xanh', kind: 'leaf', cost: 5, grow: 15, yield: 3, lvl: 1, color: '#6E9F4B' },
    lemon:   { name: 'Chanh', kind: 'fruit', cost: 6, grow: 12, yield: 2, lvl: 1, color: '#D6C24A' },
    black:   { name: 'Trà đen', kind: 'leaf', cost: 8, grow: 18, yield: 3, lvl: 2, color: '#4F6B3A' },
    jasmine: { name: 'Hoa nhài', kind: 'flower', cost: 6, grow: 12, yield: 2, lvl: 2, color: '#F4F1E4' },
    peach:   { name: 'Đào', kind: 'fruit', cost: 8, grow: 14, yield: 2, lvl: 2, color: '#E39B62' },
    oolong:  { name: 'Ô long', kind: 'leaf', cost: 10, grow: 20, yield: 3, lvl: 3, color: '#5C8A4A' },
    rose:    { name: 'Hoa hồng', kind: 'flower', cost: 6, grow: 12, yield: 2, lvl: 3, color: '#D98BA0' },
    white:   { name: 'Trà trắng', kind: 'leaf', cost: 12, grow: 22, yield: 3, lvl: 4, color: '#9CB98A' },
    lychee:  { name: 'Vải', kind: 'fruit', cost: 10, grow: 14, yield: 2, lvl: 4, color: '#E9A8A6' },
  };
  const ROUTES = {
    green:  ['Heat fixation', 'Rolling', 'Drying'],
    black:  ['Withering', 'Rolling', 'Oxidation', 'Drying'],
    oolong: ['Withering', 'Bruising', 'Fixation', 'Rolling', 'Drying'],
    white:  ['Withering', 'Drying'],
  };
  const ALL_STEPS = ['Withering', 'Heat fixation', 'Fixation', 'Rolling', 'Bruising', 'Oxidation', 'Drying', 'Roasting'];
  // Thuộc tính vị cho Blending Lab (0–100): sweetness, acidity, strength, aroma (Floral 0 → Fruity 100)
  const FLAVOR = {
    green:   { s: 20, a: 20, t: 60, r: 35 }, black: { s: 25, a: 20, t: 90, r: 55 },
    oolong:  { s: 30, a: 15, t: 75, r: 30 }, white: { s: 30, a: 15, t: 35, r: 15 },
    peach:   { s: 88, a: 30, t: 0, r: 95 }, lemon: { s: 10, a: 95, t: 0, r: 80 },
    lychee:  { s: 82, a: 25, t: 0, r: 75 }, jasmine: { s: 40, a: 10, t: 5, r: 0 }, rose: { s: 45, a: 15, t: 5, r: 5 },
  };
  const ORDERS = [
    { q: 'Mình muốn thứ gì đó thơm trái cây, sảng khoái và không quá ngọt.', req: { r: 'High', a: 'Medium', s: 'Low', t: 'Light' } },
    { q: 'Một ly trà đậm vị, ít ngọt cho buổi sáng nhé.', req: { t: 'Strong', s: 'Low' } },
    { q: 'Cho mình ly gì thơm hoa, nhẹ nhàng thôi.', req: { r: 'Low', t: 'Light' } },
    { q: 'Ngọt ngọt, thơm đào thì tuyệt!', req: { s: 'High', r: 'High' } },
    { q: 'Chua chua cho tỉnh ngủ đi bạn ơi.', req: { a: 'High' } },
    { q: 'Cân bằng thôi, không gì quá nổi bật.', req: { s: 'Medium', a: 'Medium', t: 'Medium' } },
  ];
  const LEVEL_VAL = { Low: 20, Light: 20, Medium: 50, High: 80, Strong: 80 };
  const DIM_NAME = { s: 'Sweetness', a: 'Acidity', t: 'Tea Strength', r: 'Aroma (Fruity)' };

  // ---------------------------- Trạng thái ----------------------------
  const today = () => new Date().toISOString().slice(0, 10);
  function fresh() {
    return {
      v: 1, coins: 60, xp: 0, level: 1, savedAt: 0,
      plots: Array.from({ length: 12 }, () => ({ crop: null, plantedAt: 0, wateredAt: 0 })),
      items: { green: 0, black: 0, oolong: 0, white: 0, lemon: 0, peach: 0, lychee: 0, jasmine: 0, rose: 0 },
      teas: {},          // trà đã chế biến: { green: [quality, ...] }
      journal: [],       // sản phẩm đã tạo
      blend: { base: null, mix: { tea: 60, peach: 20, jasmine: 10, lemon: 10 } },
      order: 0,
      daily: { date: today(), water: 0, harvest: 0, process: 0, serve: 0, claimed: [] },
    };
  }
  let S = load();
  let seed = 'green';

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) return Object.assign(fresh(), JSON.parse(raw));
    } catch (e) { /* localStorage có thể bị chặn */ }
    return fresh();
  }
  let syncTimer = null;
  function save() {
    S.savedAt = Date.now();
    try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* bỏ qua */ }
    if (AUTH) {
      clearTimeout(syncTimer);
      syncTimer = setTimeout(() => {
        fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(S) }).catch(() => {});
      }, 800);
    }
  }
  async function pullServer() {
    if (!AUTH) return;
    try {
      const res = await fetch(API);
      const data = await res.json();
      if (data.ok && data.state && (data.state.savedAt || 0) > (S.savedAt || 0)) {
        S = Object.assign(fresh(), data.state);
        renderAll();
      } else save();
    } catch (e) { /* offline */ }
  }

  const levelInfo = () => LEVELS.slice().reverse().find((l) => S.xp >= l.xp);
  function toast(msg) {
    const t = $('#toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 2200);
  }
  function addXP(n, why) {
    const before = levelInfo().lvl;
    S.xp += n;
    const after = levelInfo();
    S.level = after.lvl;
    if (after.lvl > before) toast(`🎉 Lên cấp ${after.lvl}: ${after.title}!`);
    else if (why) toast(`+${n} XP · ${why}`);
  }
  function resetDaily() { if (S.daily.date !== today()) S.daily = { date: today(), water: 0, harvest: 0, process: 0, serve: 0, claimed: [] }; }
  const TASKS = [
    { id: 'water', label: 'Tưới 3 cây', goal: 3, xp: 10 }, { id: 'harvest', label: 'Thu hoạch 5 lần', goal: 5, xp: 20 },
    { id: 'process', label: 'Chế biến 1 mẻ trà', goal: 1, xp: 30 }, { id: 'serve', label: 'Phục vụ 1 đơn', goal: 1, xp: 20 },
  ];
  function track(id) {
    resetDaily();
    S.daily[id] += 1;
    const t = TASKS.find((x) => x.id === id);
    if (t && S.daily[id] >= t.goal && !S.daily.claimed.includes(id)) {
      S.daily.claimed.push(id); S.xp += t.xp; S.level = levelInfo().lvl;
      setTimeout(() => toast(`✅ Daily task: ${t.label} · +${t.xp} XP`), 900);
    }
  }

  // ---------------------------- Header & sidebar ----------------------------
  function renderTop() {
    const info = levelInfo();
    const next = LEVELS.find((l) => l.lvl === info.lvl + 1);
    $('#g-title').textContent = info.title;
    $('#g-level').textContent = info.lvl;
    $('#g-coins').textContent = S.coins;
    $('#g-leaves').textContent = S.items.green + S.items.black + S.items.oolong + S.items.white;
    if (next) {
      const pct = ((S.xp - info.xp) / (next.xp - info.xp)) * 100;
      $('#g-xpbar').style.width = pct + '%';
      $('#g-xptext').textContent = `${S.xp} XP · còn ${next.xp - S.xp} XP lên cấp ${next.lvl}`;
    } else { $('#g-xpbar').style.width = '100%'; $('#g-xptext').textContent = `${S.xp} XP · cấp tối đa`; }
    $$('.game-tabs button[data-lvl]').forEach((b) => {
      const need = Number(b.dataset.lvl);
      b.disabled = info.lvl < need;
      b.title = b.disabled ? `Mở khóa ở cấp ${need}` : '';
    });
  }
  function renderSide() {
    resetDaily();
    $('#tasks').innerHTML = TASKS.map((t) => {
      const v = Math.min(S.daily[t.id], t.goal);
      return `<div class="task ${v >= t.goal ? 'done' : ''}"><span>${t.label} (${v}/${t.goal})</span><span>+${t.xp} XP</span></div>`;
    }).join('');
    const teaCount = Object.values(S.teas).reduce((a, b) => a + b.length, 0);
    $('#inventory').innerHTML = Object.keys(S.items).map((k) => `<div><span>${CROPS[k].name}</span><strong>${S.items[k]}</strong></div>`).join('') +
      `<div style="grid-column: 1/-1"><span>Mẻ trà đã chế biến</span><strong>${teaCount}</strong></div>`;
  }

  // ---------------------------- A. Garden ----------------------------
  function plantSVG(p) {
    const c = CROPS[p.crop];
    const st = stage(p);
    if (st.k === 'seed') return '<svg viewBox="0 0 60 60" width="60"><ellipse cx="30" cy="48" rx="14" ry="5" fill="#6B4E36"/></svg>';
    const h = st.k === 'ready' ? 1 : 0.35 + 0.6 * st.pct;
    const leaf = c.kind === 'leaf' ? c.color : '#6E9F4B';
    const deco = st.k === 'ready' && c.kind !== 'leaf'
      ? `<circle cx="22" cy="${46 - 30 * h}" r="5" fill="${c.color}" stroke="#fff"/><circle cx="38" cy="${50 - 26 * h}" r="5" fill="${c.color}" stroke="#fff"/>` : '';
    return `<svg viewBox="0 0 60 60" width="64"><path d="M30 52 V${52 - 34 * h}" stroke="#4F6B3A" stroke-width="3"/>
      <ellipse cx="22" cy="${50 - 22 * h}" rx="${8 * h + 3}" ry="${4 * h + 2}" fill="${leaf}" transform="rotate(-25 22 ${50 - 22 * h})"/>
      <ellipse cx="38" cy="${50 - 18 * h}" rx="${8 * h + 3}" ry="${4 * h + 2}" fill="${leaf}" transform="rotate(25 38 ${50 - 18 * h})"/>
      <ellipse cx="30" cy="${52 - 34 * h}" rx="${6 * h + 2}" ry="${8 * h + 2}" fill="${leaf}"/>${deco}</svg>`;
  }
  function stage(p) {
    if (!p.crop) return { k: 'empty' };
    if (!p.wateredAt) return { k: 'seed' };
    const pct = Math.min(1, (Date.now() - p.wateredAt) / (CROPS[p.crop].grow * 1000));
    return pct >= 1 ? { k: 'ready', pct: 1 } : { k: 'growing', pct };
  }
  function renderSeeds() {
    const lvl = levelInfo().lvl;
    $('#seed-picker').innerHTML = Object.entries(CROPS).map(([k, c]) => {
      const locked = lvl < c.lvl;
      return `<button data-seed="${k}" class="${seed === k ? 'active' : ''}" ${locked ? 'disabled title="Mở ở cấp ' + c.lvl + '"' : ''}>${c.name} · ${c.cost}🪙${locked ? ' 🔒' : ''}</button>`;
    }).join('');
  }
  function renderPlots() {
    const info = levelInfo();
    const open = info.plots;
    const next = LEVELS.find((l) => l.lvl === info.lvl + 1);
    const shown = next ? next.plots : open;
    $('#plots').innerHTML = S.plots.slice(0, shown).map((p, i) => {
      if (i >= open) return `<div class="plot locked" aria-disabled="true"><span class="plot-label">🔒 Cấp ${next.lvl}</span></div>`;
      const st = stage(p);
      let label = 'Luống trống – gieo hạt';
      if (st.k === 'seed') label = `${CROPS[p.crop].name} · cần tưới 💧`;
      if (st.k === 'growing') label = `${CROPS[p.crop].name} · ${Math.ceil(CROPS[p.crop].grow * (1 - st.pct))}s`;
      if (st.k === 'ready') label = `${CROPS[p.crop].name} · Thu hoạch!`;
      const bar = st.k === 'growing' ? `<span class="grow"><i style="width:${st.pct * 100}%"></i></span>` : '';
      return `<button class="plot ${st.k === 'ready' ? 'ready' : ''}" data-plot="${i}" aria-label="${esc(label)}">${bar}
        ${p.crop ? `<span class="plant">${plantSVG(p)}</span>` : ''}<span class="plot-label">${esc(label)}</span></button>`;
    }).join('');
  }
  function water(i) {
    const p = S.plots[i];
    if (p.crop && !p.wateredAt) { p.wateredAt = Date.now(); S.xp += 3; S.level = levelInfo().lvl; track('water'); return true; }
    return false;
  }
  $('#seed-picker').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-seed]'); if (!b || b.disabled) return;
    seed = b.dataset.seed; renderSeeds();
  });
  $('#plots').addEventListener('click', (e) => {
    const b = e.target.closest('[data-plot]'); if (!b) return;
    const i = Number(b.dataset.plot); const p = S.plots[i]; const st = stage(p);
    if (st.k === 'empty') {
      const c = CROPS[seed];
      if (S.coins < c.cost) { toast('Không đủ Tea Coins. Hãy bán bớt lá hoặc phục vụ khách.'); return; }
      S.coins -= c.cost; p.crop = seed; p.plantedAt = Date.now(); p.wateredAt = 0;
      toast(`Đã gieo ${c.name}. Bấm lần nữa để tưới.`);
    } else if (st.k === 'seed') { water(i); toast('💧 Đã tưới. Cây đang lớn…'); }
    else if (st.k === 'growing') { toast('Cây đang lớn, quay lại sau ít giây nhé.'); return; }
    else if (st.k === 'ready') {
      const c = CROPS[p.crop];
      S.items[p.crop] += c.yield; p.crop = null; p.wateredAt = 0;
      track('harvest'); addXP(15, `Thu hoạch ${c.yield} ${c.name}`);
    }
    save(); renderAll();
  });
  $('#water-all').addEventListener('click', () => {
    let n = 0; S.plots.slice(0, levelInfo().plots).forEach((_, i) => { if (water(i)) n++; });
    toast(n ? `💧 Đã tưới ${n} cây` : 'Không có cây nào cần tưới'); save(); renderAll();
  });
  $('#sell-leaves').addEventListener('click', () => {
    const order = ['green', 'black', 'oolong', 'white']; let left = 5;
    const total = order.reduce((a, k) => a + S.items[k], 0);
    if (total < 5) { toast('Cần ít nhất 5 lá trà để bán.'); return; }
    order.forEach((k) => { const take = Math.min(S.items[k], left); S.items[k] -= take; left -= take; });
    S.coins += 10; toast('+10 🪙'); save(); renderAll();
  });

  // ---------------------------- B. Processing ----------------------------
  let proc = null; let heatRAF = null;
  function renderProcTypes() {
    $('#proc-types').innerHTML = Object.keys(ROUTES).map((k) =>
      `<button data-proc="${k}" ${S.items[k] < 3 ? 'disabled' : ''}>${CROPS[k].name} (${S.items[k]} lá)</button>`).join('');
  }
  function shuffle(a) { return a.map((x) => [Math.random(), x]).sort((p, q) => p[0] - q[0]).map((x) => x[1]); }
  function startProc(type) {
    const route = ROUTES[type];
    const extra = shuffle(ALL_STEPS.filter((s) => !route.includes(s))).slice(0, 2);
    proc = { type, chain: [], options: shuffle(route.concat(extra)) };
    $('#proc-work').classList.remove('hidden'); $('#proc-timing').classList.add('hidden'); $('#proc-result').textContent = '';
    renderProc();
  }
  function renderProc() {
    $('#proc-chain').innerHTML = ['Harvest'].concat(proc.chain).map((s) => `<span class="pill pill-dark">${s}</span>`).join(' → ');
    $('#proc-steps').innerHTML = proc.options.map((s) => `<button data-step="${s}" class="${proc.chain.includes(s) ? 'used' : ''}">${s}</button>`).join('') +
      `<button data-step="__done" ${proc.chain.length ? '' : 'disabled'}>✔ Chốt chuỗi</button>`;
  }
  $('#proc-types').addEventListener('click', (e) => { const b = e.target.closest('[data-proc]'); if (b && !b.disabled) startProc(b.dataset.proc); });
  $('#proc-steps').addEventListener('click', (e) => {
    const b = e.target.closest('[data-step]'); if (!b || !proc) return;
    if (b.dataset.step === '__done') { startHeat(); return; }
    proc.chain.push(b.dataset.step); renderProc();
  });
  $('#proc-reset').addEventListener('click', () => { if (proc) { proc.chain = []; renderProc(); $('#proc-timing').classList.add('hidden'); cancelAnimationFrame(heatRAF); } });
  function startHeat() {
    $('#proc-timing').classList.remove('hidden');
    const start = 30 + Math.random() * 40; proc.zone = [start, start + 16];
    const z = $('#heat-zone'); z.style.left = start + '%'; z.style.width = '16%';
    const t0 = performance.now();
    cancelAnimationFrame(heatRAF);
    const loop = (t) => { proc.mark = (Math.sin((t - t0) / 600) * 0.5 + 0.5) * 100; $('#heat-mark').style.left = proc.mark + '%'; heatRAF = requestAnimationFrame(loop); };
    heatRAF = requestAnimationFrame(loop);
  }
  $('#proc-finish').addEventListener('click', () => {
    if (!proc) return; cancelAnimationFrame(heatRAF);
    const route = ROUTES[proc.type];
    let correct = 0; route.forEach((s, i) => { if (proc.chain[i] === s) correct++; });
    const orderScore = (correct / Math.max(route.length, proc.chain.length)) * 70;
    const inZone = proc.mark >= proc.zone[0] && proc.mark <= proc.zone[1];
    const dist = inZone ? 0 : Math.min(Math.abs(proc.mark - proc.zone[0]), Math.abs(proc.mark - proc.zone[1]));
    const timing = Math.max(0, 30 - dist);
    const quality = Math.round(orderScore + timing);
    S.items[proc.type] -= 3;
    (S.teas[proc.type] = S.teas[proc.type] || []).push(quality);
    S.journal.unshift({ name: `${CROPS[proc.type].name} chế biến`, detail: `Chất lượng ${quality}%`, at: Date.now() });
    track('process'); addXP(25, 'Chế biến 1 mẻ trà');
    const right = `Quy trình đúng: Harvest → ${route.join(' → ')}`;
    $('#proc-result').innerHTML = `<strong>Chất lượng ${quality}%</strong> · ${correct}/${route.length} công đoạn đúng vị trí, ${inZone ? 'canh thời điểm chuẩn' : 'lệch thời điểm'}.<br><span class="muted">${right}</span>`;
    proc = null; $('#proc-work').classList.add('hidden');
    save(); renderAll();
  });

  // ---------------------------- C. Blending Lab ----------------------------
  const BLEND_KEYS = ['tea', 'peach', 'lemon', 'lychee', 'jasmine', 'rose'];
  function renderBlend() {
    const bases = Object.keys(S.teas).filter((k) => S.teas[k].length);
    if (!S.blend.base || !bases.includes(S.blend.base)) S.blend.base = bases[0] || null;
    $('#blend-base').innerHTML = bases.length
      ? bases.map((k) => `<option value="${k}" ${S.blend.base === k ? 'selected' : ''}>${CROPS[k].name} (${S.teas[k].length} mẻ, tốt nhất ${Math.max(...S.teas[k])}%)</option>`).join('')
      : '<option value="">Chưa có trà đã chế biến – vào Processing House</option>';
    const lvl = levelInfo().lvl;
    $('#blend-rows').innerHTML = BLEND_KEYS.map((k) => {
      const crop = k === 'tea' ? null : CROPS[k];
      const locked = crop && lvl < crop.lvl;
      const v = S.blend.mix[k] || 0;
      const label = k === 'tea' ? 'Trà nền' : crop.name + (locked ? ' 🔒' : ` (${S.items[k]})`);
      return `<div class="blend-row"><label for="b-${k}" class="small">${label}</label>
        <input class="plain" type="range" id="b-${k}" data-k="${k}" min="0" max="100" step="5" value="${v}" ${locked ? 'disabled' : ''}>
        <span class="num small"><strong>${v}%</strong></span></div>`;
    }).join('');
    renderProfile();
  }
  function blendProfile() {
    const base = S.blend.base || 'green';
    let tot = { s: 0, a: 0, t: 0, r: 0 };
    BLEND_KEYS.forEach((k) => {
      const w = (S.blend.mix[k] || 0) / 100;
      const f = FLAVOR[k === 'tea' ? base : k];
      Object.keys(tot).forEach((d) => { tot[d] += f[d] * w; });
    });
    // độ đậm trà phụ thuộc tỷ lệ trà nền
    tot.t = FLAVOR[base].t * ((S.blend.mix.tea || 0) / 100) * 1.3;
    Object.keys(tot).forEach((d) => { tot[d] = Math.round(Math.max(0, Math.min(100, tot[d]))); });
    return tot;
  }
  const lvlWord = (v, d) => (v < 35 ? (d === 't' ? 'Light' : 'Low') : v > 65 ? (d === 't' ? 'Strong' : 'High') : 'Medium');
  function renderProfile() {
    const p = blendProfile();
    $('#blend-profile').innerHTML = Object.keys(p).map((d) => `<span class="pill">${DIM_NAME[d]}: ${lvlWord(p[d], d)} (${p[d]})</span>`).join('');
  }
  $('#blend-rows').addEventListener('input', (e) => {
    const el = e.target.closest('input[data-k]'); if (!el) return;
    const k = el.dataset.k; const val = Number(el.value);
    const others = BLEND_KEYS.filter((x) => x !== k && !document.getElementById('b-' + x).disabled);
    const rest = others.reduce((a, x) => a + (S.blend.mix[x] || 0), 0);
    const remain = 100 - val;
    S.blend.mix[k] = val;
    others.forEach((x) => { S.blend.mix[x] = rest ? Math.round(((S.blend.mix[x] || 0) / rest) * remain) : Math.round(remain / others.length); });
    const sum = BLEND_KEYS.reduce((a, x) => a + (S.blend.mix[x] || 0), 0);
    if (sum !== 100 && others.length) S.blend.mix[others[0]] += 100 - sum;
    renderBlend(); save();
  });
  $('#blend-base').addEventListener('change', (e) => { S.blend.base = e.target.value; renderProfile(); save(); });

  // ---------------------------- D. Tea House ----------------------------
  function currentOrder() {
    const special = levelInfo().lvl >= 5;
    const o = ORDERS[S.order % ORDERS.length];
    return Object.assign({ special }, o);
  }
  function renderOrder() {
    const o = currentOrder();
    $('#order').innerHTML = `<div class="btn-row" style="justify-content:space-between"><strong>Customer Order #${String(S.order + 1).padStart(3, '0')}</strong>
      <span class="pill ${o.special ? 'pill-terra' : ''}">${o.special ? 'Đơn đặc biệt ×1.5' : 'Đơn mới'}</span></div>
      <blockquote>“${esc(o.q)}”</blockquote>
      <div class="pills">${Object.entries(o.req).map(([d, v]) => `<span class="pill pill-sage">${DIM_NAME[d]}: ${v}</span>`).join('')}</div>`;
  }
  function recipeLinkFor() {
    const m = S.blend.mix; const b = S.blend.base;
    if (b === 'oolong' && m.peach >= 15) return 'tra-dao-o-long';
    if (m.lychee >= 15 || m.jasmine >= 20) return 'tra-vai-lai';
    if (m.lemon >= 15) return 'tra-chanh-mat-ong';
    if (b === 'black') return 'tra-den-cam-que';
    if (b === 'white' || m.rose >= 15) return 'tra-trang-hoa-hong';
    if (b === 'oolong') return 'o-long-rang-nguyen-ban';
    return 'tra-xanh-cold-brew-bac-ha';
  }
  $('#serve').addEventListener('click', () => {
    const base = S.blend.base;
    if (!base || !S.teas[base] || !S.teas[base].length) { toast('Cần trà đã chế biến – vào Processing House trước.'); return; }
    const used = BLEND_KEYS.filter((k) => k !== 'tea' && (S.blend.mix[k] || 0) > 0);
    const missing = used.filter((k) => S.items[k] < 1);
    if (missing.length) { toast('Thiếu nguyên liệu: ' + missing.map((k) => CROPS[k].name).join(', ')); return; }
    const o = currentOrder(); const p = blendProfile();
    const diffs = Object.entries(o.req).map(([d, v]) => Math.abs(p[d] - LEVEL_VAL[v]));
    const match = Math.round(100 - diffs.reduce((a, b) => a + b, 0) / diffs.length);
    const q = S.teas[base].sort((a, b) => b - a).shift(); // dùng mẻ tốt nhất
    const score = Math.max(0, Math.round(match * 0.75 + q * 0.25));
    const coins = Math.round((score / 100) * 40 * (o.special ? 1.5 : 1));
    used.forEach((k) => { S.items[k] -= 1; });
    S.coins += coins; S.order += 1;
    const slug = recipeLinkFor();
    S.journal.unshift({ name: `Blend ${CROPS[base].name}` + (used.length ? ' + ' + used.map((k) => CROPS[k].name).join(', ') : ''),
      detail: `Phục vụ khách · điểm ${score}/100`, slug, at: Date.now() });
    track('serve'); addXP(score >= 70 ? 40 : 25, `Phục vụ khách · ${score} điểm`);
    $('#serve-result').innerHTML = `Điểm phục vụ <strong>${score}/100</strong> (độ khớp yêu cầu ${match}%, chất lượng trà ${q}%) · +${coins} 🪙.
      <a href="${RECIPE_LINKS[slug]}">Xem công thức thật gần nhất →</a>`;
    save(); renderAll();
  });
  $('#skip-order').addEventListener('click', () => { S.order += 1; save(); renderOrder(); });

  // ---------------------------- E. Journal ----------------------------
  function renderJournal() {
    const seeds = Object.entries(CROPS).map(([k, c]) => `<span class="pill ${levelInfo().lvl >= c.lvl ? 'pill-sage' : ''}">${c.name}${levelInfo().lvl >= c.lvl ? '' : ' 🔒'}</span>`).join('');
    const items = S.journal.slice(0, 20).map((j) => `<div class="task"><span><strong>${esc(j.name)}</strong> <span class="pill">Game Recipe</span><br><span class="muted">${esc(j.detail)}</span></span>
      ${j.slug && RECIPE_LINKS[j.slug] ? `<a class="small" href="${RECIPE_LINKS[j.slug]}">Công thức thật →</a>` : ''}</div>`).join('');
    $('#journal').innerHTML = `<p class="label">Giống trà & nguyên liệu</p><div class="pills mb-2">${seeds}</div>
      <p class="label">Sản phẩm đã tạo</p>${items || '<p class="muted small">Chưa có sản phẩm nào.</p>'}
      <button class="btn btn-ghost btn-small mt-1" id="reset-game">Chơi lại từ đầu</button>`;
    $('#reset-game').addEventListener('click', () => { if (confirm('Xóa toàn bộ tiến trình Tea Garden?')) { S = fresh(); save(); renderAll(); } });
  }

  // ---------------------------- Tabs & vòng lặp ----------------------------
  let tab = 'garden';
  $$('.game-tabs button').forEach((b) => b.addEventListener('click', () => {
    if (b.disabled) return;
    tab = b.dataset.tab;
    $$('.game-tabs button').forEach((x) => x.classList.toggle('active', x === b));
    $$('.g-panel').forEach((p) => p.classList.toggle('hidden', p.dataset.panel !== tab));
    renderAll();
  }));
  function renderAll() {
    renderTop(); renderSide(); renderSeeds(); renderPlots();
    if (tab === 'process') renderProcTypes();
    if (tab === 'blend') renderBlend();
    if (tab === 'house') renderOrder();
    if (tab === 'journal') renderJournal();
  }
  setInterval(() => { if (tab === 'garden') renderPlots(); }, 1000);
  renderAll();
  pullServer();
})();
