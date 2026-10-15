/* Keeps the books and the site from being copied the easy way: no right click, no text selection on reading
   pages, no copy, no save or print shortcuts, no image dragging. Inputs and forms keep working normally. */
(function () {
  const free = el => el && el.closest && el.closest('input, textarea, select, [contenteditable], .selectable, .admin');
  const guarded = el => el && el.closest && el.closest('.guarded');
  document.addEventListener('contextmenu', e => { if (!free(e.target)) e.preventDefault(); });
  document.addEventListener('dragstart', e => { if (e.target && (e.target.tagName === 'IMG' || e.target.tagName === 'VIDEO' || guarded(e.target))) e.preventDefault(); });
  ['copy', 'cut'].forEach(t => document.addEventListener(t, e => {
    const sel = document.getSelection && document.getSelection();
    const node = sel && sel.anchorNode && (sel.anchorNode.nodeType === 1 ? sel.anchorNode : sel.anchorNode.parentElement);
    if (!free(node)) { e.preventDefault(); if (e.clipboardData) e.clipboardData.setData('text/plain', ''); }
  }));
  document.addEventListener('selectstart', e => { const n = e.target.nodeType === 1 ? e.target : e.target.parentElement; if (guarded(n) && !free(n)) e.preventDefault(); });
  document.addEventListener('keydown', e => {
    const k = (e.key || '').toLowerCase(), mod = e.ctrlKey || e.metaKey;
    if (free(e.target)) return;
    if ((mod && ['s', 'p', 'u', 'c', 'x', 'a'].includes(k)) || (mod && e.shiftKey && ['i', 'j', 'c'].includes(k)) || k === 'f12' || k === 'printscreen') {
      e.preventDefault(); e.stopPropagation();
    }
  }, true);
  addEventListener('beforeprint', () => document.documentElement.classList.add('printing'));
  addEventListener('afterprint', () => document.documentElement.classList.remove('printing'));
})();
