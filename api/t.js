// Anonymous visit and reading statistics. Adds the country and city Vercel already knows, hashes the IP
// (never stored in clear) and hands the event to the backend. No cookies. Bots are ignored.
const crypto = require('node:crypto');

const SB = 'https://qytpqmgzphiuhlwkybiy.supabase.co/rest/v1/rpc/pf_track';
const PK = 'sb_publishable_QgRtb2_rjK2-hMG0s4i2Bw_Y11M05_X';
const KINDS = new Set(['view', 'read', 'donate', 'donate_go', 'play', 'outbound']);

function readBody(req) {
  return new Promise(resolve => {
    if (req.body && typeof req.body === 'object') return resolve(req.body);
    if (typeof req.body === 'string') { try { return resolve(JSON.parse(req.body)); } catch (e) { return resolve({}); } }
    let raw = '';
    req.on('data', c => { raw += c; if (raw.length > 4000) req.destroy(); });
    req.on('end', () => { try { resolve(JSON.parse(raw || '{}')); } catch (e) { resolve({}); } });
    req.on('error', () => resolve({}));
  });
}

const s = (v, n) => (typeof v === 'string' ? v.slice(0, n) : null);

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.statusCode = 405; return res.end(); }
  const h = req.headers;
  const ua = h['user-agent'] || '';
  if (!ua || /bot|crawl|spider|slurp|preview|headless|lighthouse|python|curl|wget|httpclient/i.test(ua)) { res.statusCode = 204; return res.end(); }
  const b = await readBody(req);
  const kind = KINDS.has(b.kind) ? b.kind : 'view';
  const ip = String(h['x-forwarded-for'] || h['x-real-ip'] || '').split(',')[0].trim();
  let city = h['x-vercel-ip-city'] || '';
  try { city = decodeURIComponent(city); } catch (e) {}
  const p = {
    kind, path: s(b.path, 200), book: s(b.book, 60),
    chapter: Number.isInteger(b.chapter) ? String(b.chapter) : null,
    seconds: Number.isInteger(b.seconds) ? String(Math.min(b.seconds, 3600)) : null,
    visitor: s(b.visitor, 40), session: s(b.session, 40), referrer: s(b.referrer, 200),
    device: s(b.device, 20), browser: s(b.browser, 30), lang: s(b.lang, 10),
    country: s(h['x-vercel-ip-country'], 4), region: s(h['x-vercel-ip-country-region'], 60), city: s(city, 80),
    ipkey: crypto.createHash('sha256').update((ip || 'none') + 'pf-salt-2026').digest('hex'),
  };
  try {
    await fetch(SB, { method: 'POST', headers: { apikey: PK, 'Content-Type': 'application/json' }, body: JSON.stringify({ p }) });
  } catch (e) {}
  res.statusCode = 204;
  res.end();
};
