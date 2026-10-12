import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';

// Serve assets and public directory
app.use('/assets', express.static(path.join(__dirname, 'assets')));
app.use('/public', express.static(path.join(__dirname, 'public')));

// Specific text and xml files
const directFiles = [
  'robots.txt',
  'sitemap.xml',
  'llms.txt',
  'llms-full.txt',
  'BingSiteAuth.xml',
  'screenshot.png',
  'qefro-hero-3d-v3.png'
];

for (const file of directFiles) {
  app.get(`/${file}`, (req, res) => {
    res.sendFile(path.join(__dirname, file));
  });
}

// Redirect *.html to clean URL (e.g. /pricing.html -> /pricing, /index.html -> /)
app.use((req, res, next) => {
  if (req.path.endsWith('.html')) {
    if (req.path === '/index.html') {
      return res.redirect(301, '/');
    }
    const cleanPath = req.path.replace(/\.html$/, '');
    const query = req.url.slice(req.path.length);
    return res.redirect(301, cleanPath + query);
  }
  next();
});

// Trailing slash normalization (except root /)
app.use((req, res, next) => {
  if (req.path !== '/' && req.path.endsWith('/')) {
    const query = req.url.slice(req.path.length);
    return res.redirect(301, req.path.slice(0, -1) + query);
  }
  next();
});

// Root route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Dynamic route matching for HTML files and root static files
app.use((req, res, next) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return next();
  }

  const slug = req.path.replace(/^\//, '');
  if (!slug) return next();

  const candidateHtml = path.join(__dirname, `${slug}.html`);
  if (fs.existsSync(candidateHtml) && fs.statSync(candidateHtml).isFile()) {
    return res.sendFile(candidateHtml);
  }

  const candidateDirect = path.join(__dirname, slug);
  if (fs.existsSync(candidateDirect) && fs.statSync(candidateDirect).isFile()) {
    return res.sendFile(candidateDirect);
  }

  next();
});

// 404 handler
app.use((req, res) => {
  const notFoundPath = path.join(__dirname, '404.html');
  if (fs.existsSync(notFoundPath)) {
    res.status(404).sendFile(notFoundPath);
  } else {
    res.status(404).send('Page Not Found');
  }
});

app.listen(PORT, HOST, () => {
  console.log(`Qefro server running on http://${HOST}:${PORT}`);
});
