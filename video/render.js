// Rend film.html en MP4 image par image (30 i/s), avec la voix off si elle est fournie.
// Prérequis : ffmpeg, playwright-core (npm install) et Google Chrome. Le script sert lui-même le dépôt en local.
// Usage : node render.js 169|11 [voix.m4a] [--en] [--stills 1,12,24]   (--en : textes anglais, fichiers en « -en »)
const { chromium } = require('playwright-core');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path'), http = require('http');

const fmt = process.argv[2] === '11' ? '11' : '169';
const voice = process.argv.slice(3).find(a => !a.startsWith('--') && !/^[\d.,]+$/.test(a));
const si = process.argv.indexOf('--stills');
const stills = si > 0 ? process.argv[si + 1].split(',').map(Number) : null;
const FPS = 30;
const EN = process.argv.includes('--en'), SUF = EN ? '-en' : '';
const outDir = path.join(__dirname, 'out'); fs.mkdirSync(outDir, { recursive: true });

/* Petit serveur local, le temps du rendu : la racine du dépôt, en lecture seule */
const ROOT = path.join(__dirname, '..');
const TYPES = { '.html':'text/html; charset=utf-8', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.mp4':'video/mp4', '.png':'image/png', '.webp':'image/webp', '.jpg':'image/jpeg', '.svg':'image/svg+xml', '.woff2':'font/woff2', '.vtt':'text/vtt' };
function serve() {
  const server = http.createServer((req, res) => {
    const f = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Content-Length': fs.statSync(f).size });
    fs.createReadStream(f).pipe(res);
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => r(server)));
}

(async () => {
  const server = await serve();
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const [W, H] = fmt === '11' ? [1080, 1080] : [1920, 1080];
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto(`http://127.0.0.1:${server.address().port}/video/film.html?f=${fmt}${EN ? '&lang=en' : ''}`, { waitUntil: 'networkidle' });
  await page.evaluate(() => window.ready);
  await page.evaluate(() => document.fonts.ready);

  if (stills) {
    for (const t of stills) {
      await page.evaluate(t => seek(t), t);
      await page.screenshot({ path: path.join(outDir, `still-${fmt}${SUF}-${t}.jpg`), type: 'jpeg', quality: 85 });
    }
    await browser.close(); server.close(); return;
  }

  /* Miniature : la première image (couverture), en PNG pour LinkedIn et comme pochette du MP4 */
  const name = fmt === '11' ? '1x1' : '16x9';
  const thumb = path.join(outDir, `miniature-${name}${SUF}.png`);
  await page.evaluate(() => seek(0.1));
  await page.screenshot({ path: thumb, type: 'png' });

  const total = Math.round(await page.evaluate(() => DURATION) * FPS);
  const file = path.join(outDir, `synapses-${name}${SUF}${voice ? '' : '-sans-voix'}.mp4`);
  const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
  if (voice) args.push('-i', voice);
  args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart');
  /* La voix est complétée par du silence jusqu’à la fin de l’image */
  if (voice) args.push('-af', 'apad', '-c:a', 'aac', '-b:a', '192k', '-shortest');
  const raw = file.replace(/\.mp4$/, '.tmp.mp4');
  args.push(raw);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => seek(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) process.stdout.write(`${fmt} ${Math.round(i / total * 100)} %\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close(); server.close();
  /* Pochette intégrée (Finder, VLC…) ; les messageries, elles, prennent la première image, qui est déjà la couverture */
  const mux = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-i', raw, '-i', thumb, '-map', '0', '-map', '1', '-c', 'copy',
    '-disposition:v:1', 'attached_pic', '-movflags', '+faststart', file], { stdio: 'inherit' });
  await new Promise(r => mux.on('close', r));
  fs.rmSync(raw);
  console.log('→', file, '\n→', thumb);
})().catch(e => { console.error(e); process.exit(1); });
