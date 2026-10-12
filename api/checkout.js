// Creates a Stripe Checkout session for a consultation or a service deposit.
// Needs STRIPE_SECRET_KEY in the Vercel project environment. Amounts are fixed here,
// never taken from the browser. No npm dependencies: Stripe's REST API over fetch.

const ITEMS = {
  consultation: { name: 'Consultation, 45 minutes', amount: 15000, desc: 'Credited to your project if you book within thirty days.' },
  platforms: { name: 'Deposit, web platforms and apps', amount: 90000, desc: 'Deposit to start the work. Credited to the final invoice.' },
  'ai-building': { name: 'Deposit, build with AI, coached', amount: 12000, desc: 'One hour, or a deposit on a workshop.' },
  'network-design': { name: 'Deposit, network design and documentation', amount: 25000, desc: 'Deposit to start the survey and design.' },
  'training-content': { name: 'Deposit, training content, labs and exam practice', amount: 30000, desc: 'Deposit to start the module.' },
  books: { name: 'Deposit, book writing, editing and production', amount: 30000, desc: 'Deposit to start the manuscript review.' },
  motion: { name: 'Deposit, motion design and video edits', amount: 15000, desc: 'Deposit to start the script and storyboard.' },
  'content-systems': { name: 'Deposit, content systems and social kits', amount: 40000, desc: 'Deposit on the first month.' },
  receptionist: { name: 'Deposit, AI phone receptionist and automation', amount: 30000, desc: 'Deposit to start the call flow design.' },
  localization: { name: 'Deposit, bilingual localisation', amount: 15000, desc: 'Deposit to start the translation.' },
};

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.statusCode = 405; return res.end(JSON.stringify({ error: 'method' })); }
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) { res.statusCode = 503; return res.end(JSON.stringify({ error: 'not_configured' })); }

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};
  const item = ITEMS[body.item];
  if (!item) { res.statusCode = 400; return res.end(JSON.stringify({ error: 'unknown_item' })); }

  const host = req.headers['x-forwarded-host'] || req.headers.host;
  const proto = req.headers['x-forwarded-proto'] || 'https';
  const origin = proto + '://' + host;

  const p = new URLSearchParams();
  p.append('mode', 'payment');
  p.append('success_url', origin + '/thanks?session_id={CHECKOUT_SESSION_ID}');
  p.append('cancel_url', origin + '/services');
  p.append('line_items[0][quantity]', '1');
  p.append('line_items[0][price_data][currency]', 'usd');
  p.append('line_items[0][price_data][unit_amount]', String(item.amount));
  p.append('line_items[0][price_data][product_data][name]', item.name);
  p.append('line_items[0][price_data][product_data][description]', item.desc);
  p.append('metadata[item]', String(body.item));
  if (body.ref && /^[A-Z0-9-]{4,40}$/.test(String(body.ref))) { p.append('client_reference_id', String(body.ref)); p.append('metadata[brief]', String(body.ref)); }
  if (body.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(body.email))) p.append('customer_email', String(body.email));

  try {
    const r = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: p.toString(),
    });
    const j = await r.json();
    if (!r.ok) { res.statusCode = 502; return res.end(JSON.stringify({ error: (j.error && j.error.message) || 'stripe_error' })); }
    res.setHeader('Content-Type', 'application/json');
    res.statusCode = 200;
    return res.end(JSON.stringify({ url: j.url }));
  } catch (e) {
    res.statusCode = 502; return res.end(JSON.stringify({ error: 'stripe_unreachable' }));
  }
};
