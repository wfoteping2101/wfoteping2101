/* Anonymous statistics: one random visitor id in this browser, one per visit, the page, where the visit came from.
   No cookies, no ads, no personal data. The owner can switch his own visits off from the admin page. */
(function () {
  const get = (k, ses) => { try { return (ses ? sessionStorage : localStorage).getItem(k); } catch (e) { return null; } };
  const put = (k, v, ses) => { try { (ses ? sessionStorage : localStorage).setItem(k, v); } catch (e) {} };
  const rid = () => (self.crypto && crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36)).replace(/-/g, '').slice(0, 20);
  let v = get('pf-v'); if (!v) { v = rid(); put('pf-v', v); }
  let s = get('pf-s', true); if (!s) { s = rid(); put('pf-s', s, true); }
  window.pfVisitor = () => v; window.pfSession = () => s;
  const ua = navigator.userAgent || '';
  const device = /iPad|Tablet/i.test(ua) ? 'tablet' : /Mobi|Android|iPhone/i.test(ua) ? 'mobile' : 'desktop';
  const browser = /Edg\//.test(ua) ? 'Edge' : /OPR\//.test(ua) ? 'Opera' : /SamsungBrowser/.test(ua) ? 'Samsung' : /Chrome\//.test(ua) ? 'Chrome' : /Firefox\//.test(ua) ? 'Firefox' : /Safari\//.test(ua) ? 'Safari' : 'Other';
  let ref = '';
  try { if (document.referrer) { const u = new URL(document.referrer); if (u.host !== location.host) ref = u.host.replace(/^www\./, ''); } } catch (e) {}
  const q = new URLSearchParams(location.search), utm = q.get('utm_source') || q.get('ref');
  if (utm) ref = ('via ' + utm).slice(0, 60);
  function send(kind, extra, beacon) {
    if (navigator.webdriver || get('pf-me') === '1' || location.pathname.startsWith('/admin')) return;
    const body = JSON.stringify(Object.assign({ kind, path: location.pathname, visitor: v, session: s, referrer: ref, device, browser,
      lang: (document.documentElement.lang || navigator.language || '').slice(0, 5) }, extra || {}));
    try {
      if (beacon && navigator.sendBeacon) { navigator.sendBeacon('/api/t', new Blob([body], { type: 'application/json' })); return; }
      fetch('/api/t', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true }).catch(() => {});
    } catch (e) {}
  }
  window.pfTrack = send;
  send('view');
  document.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('a[href^="http"]');
    if (a && !a.href.includes(location.host)) send('outbound', { book: a.hostname.slice(0, 60) }, true);
  }, { capture: true });
})();
