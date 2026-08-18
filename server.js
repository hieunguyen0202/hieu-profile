const express = require('express');
const path = require('path');
const cors = require('cors');
const profile = require('./data/profile.json');

const app = express();
const PORT = process.env.PORT || 3000;

app.disable('x-powered-by');
app.use(cors());
app.use(express.json({ limit: '32kb' }));
app.use(express.static(path.join(__dirname, 'public'), { maxAge: '1h' }));

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

app.get('/api/profile', (_req, res) => {
  res.json(profile);
});

app.post('/api/contact', (req, res) => {
  const name = String(req.body?.name || '').trim();
  const email = String(req.body?.email || '').trim();
  const message = String(req.body?.message || '').trim();

  if (!name || !email || !message) {
    return res.status(400).json({ ok: false, error: 'name, email, and message are required' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ ok: false, error: 'invalid email' });
  }

  console.log('[contact]', new Date().toISOString(), {
    name,
    email,
    message: message.slice(0, 800),
  });

  res.json({ ok: true });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Portfolio listening on http://0.0.0.0:${PORT}`);
});
