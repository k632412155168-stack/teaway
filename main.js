/* Tương tác chung: menu mobile, đóng thông báo, bộ lọc dạng drawer, chia sẻ */
(function () {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  document.querySelectorAll('.flash-close').forEach((b) =>
    b.addEventListener('click', () => b.closest('.flash').remove()));

  const filters = document.getElementById('filters');
  document.querySelectorAll('.filter-open').forEach((b) =>
    b.addEventListener('click', () => filters && filters.classList.add('open')));
  document.querySelectorAll('.filters-close').forEach((b) =>
    b.addEventListener('click', () => filters && filters.classList.remove('open')));

  document.querySelectorAll('.js-share').forEach((b) =>
    b.addEventListener('click', async () => {
      const data = { title: b.dataset.title || document.title, url: b.dataset.url || window.location.href };
      try {
        if (navigator.share) await navigator.share(data);
        else {
          await navigator.clipboard.writeText(data.url);
          const old = b.innerHTML;
          b.textContent = 'Đã sao chép liên kết';
          setTimeout(() => { b.innerHTML = old; }, 1800);
        }
      } catch (e) { /* người dùng hủy */ }
    }));

  // Xác nhận các thao tác không thể hoàn tác
  document.querySelectorAll('form[data-confirm]').forEach((f) =>
    f.addEventListener('submit', (e) => { if (!window.confirm(f.dataset.confirm)) e.preventDefault(); }));
})();
