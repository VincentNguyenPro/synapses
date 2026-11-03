// Filme l'app Synapses (réseau de démo fictif) plan par plan via le screencast CDP, puis encode chaque plan en MP4 dans clips/.
// Prérequis : ffmpeg, Google Chrome, `npm install` dans ce dossier, et un serveur local à la racine du dépôt :
//   python3 -m http.server 8765
// Usage : node video/record.js [plan …]   (sans argument : tous les plans)
// Chrome tourne en headless avec un user-agent standard, sinon Brandfetch refuse les logos.
const { chromium } = require('playwright-core');
const { execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');

const W = 1600, H = 1000, DPR = 1.5;
const CLIPS = path.join(__dirname, 'clips');
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'synapses-rec-'));
const only = process.argv.slice(2);
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* La page de l'app est servie avec, en fin de script, des crochets de pilotage (window.__S) : le fichier du dépôt n'est pas modifié. */
const END = '})();\n</script>\n</body>';
const appHtml = (() => {
  const s = fs.readFileSync(path.join(__dirname, '..', 'app', 'index.html'), 'utf8');
  const i = s.lastIndexOf(END);
  if (i < 0) throw new Error('fin de script introuvable dans app/index.html');
  return s.slice(0, i) + 'window.__S={render,load,demoContacts,clearSelection,syncChips,state,hide:()=>{demoHidden=true},unhide:()=>{demoHidden=false},nodes:()=>gNodes,contacts:()=>contacts};\n' + s.slice(i);
})();

/* Curseur visible, onde au clic, et menu déroulant dessiné (le menu natif d'un <select> n'apparaît pas dans le screencast) */
const INIT = `
(() => {
  const add = () => {
    if (document.getElementById('__cur')) return;
    const c = document.createElement('div'); c.id = '__cur';
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l15 9.5-6.6 1.4L16 20l-2.8 1.3-3.6-7.2L4 18.5z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, {position:'fixed', left:'-100px', top:'-100px', zIndex:2147483647, pointerEvents:'none', transform:'translate(-4px,-2px)', filter:'drop-shadow(0 2px 3px rgba(0,0,0,.25))'});
    document.body.appendChild(c);
    const st = document.createElement('style');
    st.textContent = '#__menu{position:fixed;z-index:2147483600;background:#fff;border:1px solid #D5DDE5;border-radius:12px;box-shadow:0 14px 34px rgba(23,33,46,.18);padding:6px;font:500 15px/1.2 Manrope,system-ui,sans-serif;color:#17212E;transform-origin:top;animation:__m .16s ease-out}' +
      '@keyframes __m{from{opacity:0;transform:scaleY(.92)}}#__menu div{padding:9px 12px 9px 32px;border-radius:8px;position:relative}#__menu div:hover{background:#E4EAFD;color:#2448C4}#__menu div.on{font-weight:800}#__menu div.on::before{content:"✓";position:absolute;left:11px;color:#2F5BEA}';
    document.head.appendChild(st);
    addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
    addEventListener('mousedown', e => {
      const r = document.createElement('div');
      Object.assign(r.style, {position:'fixed', left:e.clientX - 18 + 'px', top:e.clientY - 18 + 'px', width:'36px', height:'36px', borderRadius:'50%', border:'3px solid #2F5BEA', zIndex:2147483646, pointerEvents:'none', transition:'transform .5s ease-out, opacity .5s ease-out', transform:'scale(.3)', opacity:'1'});
      document.body.appendChild(r);
      requestAnimationFrame(() => { r.style.transform = 'scale(1.4)'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 600);
    }, true);
  };
  window.__menu = id => {
    document.getElementById('__menu')?.remove();
    const sel = document.getElementById(id), r = sel.getBoundingClientRect();
    const m = document.createElement('div'); m.id = '__menu';
    Object.assign(m.style, {left:r.left + 'px', top:r.bottom + 4 + 'px', width:r.width + 'px'});
    [...sel.options].forEach(o => {
      const d = document.createElement('div'); d.textContent = o.text; d.dataset.v = o.value;
      if (o.value === sel.value) d.className = 'on';
      d.addEventListener('click', () => { sel.value = o.value; sel.dispatchEvent(new Event('change', {bubbles:true})); m.remove(); });
      m.appendChild(d);
    });
    document.body.appendChild(m);
  };
  if (document.body) add(); else addEventListener('DOMContentLoaded', add);
})();`;

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--hide-scrollbars'] });
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR, locale: 'fr-FR',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  await ctx.addInitScript(INIT);
  const page = await ctx.newPage();
  await page.route(/supabase\.co/, r => r.abort());
  await page.route(/\/app\/(index\.html)?(#.*)?$/, r => r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: appHtml }));
  const cdp = await ctx.newCDPSession(page);
  let cur = { x: W * 0.55, y: H * 0.85 };

  let frames = null;
  cdp.on('Page.screencastFrame', f => {
    cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
    if (frames) frames.push({ t: f.metadata.timestamp, data: f.data });
  });
  async function take(name, fn) {
    if (only.length && !only.includes(name)) return;
    frames = [];
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: W * DPR, maxHeight: H * DPR, everyNthFrame: 1 });
    await sleep(300);
    await fn();
    await cdp.send('Page.stopScreencast');
    const dir = path.join(TMP, name); fs.mkdirSync(dir);
    const end = Date.now() / 1000, list = [];
    frames.forEach((f, i) => {
      const file = `f${String(i).padStart(5, '0')}.jpg`;
      fs.writeFileSync(path.join(dir, file), Buffer.from(f.data, 'base64'));
      const next = i + 1 < frames.length ? frames[i + 1].t : end;
      list.push(`file '${file}'\nduration ${Math.max(0.001, next - f.t).toFixed(4)}`);
    });
    list.push(`file 'f${String(frames.length - 1).padStart(5, '0')}.jpg'`);
    fs.writeFileSync(path.join(dir, 'list.txt'), list.join('\n') + '\n');
    frames = null;
    execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'),
      '-vf', `fps=30,scale=${W * DPR}:${H * DPR}:flags=lanczos,format=yuv420p`, '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-g', '15',
      path.join(CLIPS, name + '.mp4')]);
    console.log(name, 'ok');
  }
  async function move(x, y, ms = 700) {
    const steps = Math.max(8, Math.round(ms / 16)), a = { ...cur };
    for (let i = 1; i <= steps; i++) {
      const k = i / steps, e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      await page.mouse.move(a.x + (x - a.x) * e, a.y + (y - a.y) * e);
      await sleep(ms / steps);
    }
    cur = { x, y };
  }
  async function clickAt(x, y, ms) { await move(x, y, ms); await sleep(150); await page.mouse.down(); await sleep(70); await page.mouse.up(); }
  const centerOf = async loc => { const b = await loc.boundingBox(); return [b.x + b.width / 2, b.y + b.height / 2]; };
  /* Ouvre le menu dessiné d'un <select>, survole quelques options, puis choisit `value` */
  async function pickFrom(id, value, hover = []) {
    await page.evaluate(id => document.getElementById(id).scrollIntoView({ block: 'center' }), id);
    const [x, y] = await centerOf(page.locator('#' + id));
    await clickAt(x, y, 800);
    await page.evaluate(id => window.__menu(id), id);
    await sleep(500);
    for (const v of hover) { const [hx, hy] = await centerOf(page.locator(`#__menu div[data-v="${v}"]`)); await move(hx, hy, 350); await sleep(250); }
    const [ox, oy] = await centerOf(page.locator(`#__menu div[data-v="${value}"]`));
    await clickAt(ox, oy, 400);
  }
  /* État de départ d'un plan, réglé hors caméra */
  async function setup({ groupBy = 'sector', colorBy = 'seniority', topN = 12 } = {}) {
    await page.evaluate(({ groupBy, colorBy, topN }) => {
      __S.clearSelection();
      Object.values(__S.state.include).forEach(s => s.clear()); __S.syncChips();
      const set = (id, v, ev) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event(ev, { bubbles: true })); };
      set('topN', topN, 'input'); set('groupBy', groupBy, 'change'); set('colorBy', colorBy, 'change');
      document.querySelector('#groupBy').scrollIntoView({ block: 'center' });
    }, { groupBy, colorBy, topN });
    await sleep(1500);
  }

  await page.goto('http://localhost:8765/app/', { waitUntil: 'networkidle' });
  await sleep(1500);
  await page.mouse.move(cur.x, cur.y);
  await page.evaluate(() => { __S.hide(); __S.render(); });
  await sleep(800);

  // Regrouper par : les options, puis Fonction et Formation
  await setup();
  await take('2-regrouper', async () => {
    await pickFrom('groupBy', 'fn', ['company', 'fn', 'seniority', 'year', 'location', 'school']);
    await sleep(2200);
    await pickFrom('groupBy', 'school');
    await sleep(2400);
  });

  // Colorer par : les options, puis Fonction
  await setup();
  await take('3-colorer', async () => {
    await pickFrom('colorBy', 'fn', ['sector', 'fn', 'year', 'school']);
    await sleep(2400);
    await pickFrom('colorBy', 'year');
    await sleep(2200);
  });

  // Clic sur un secteur
  await setup();
  await take('4-secteur', async () => {
    await sleep(400);
    const [x, y] = await centerOf(page.locator('text.hubLabel').filter({ hasText: 'Tech' }).first());
    await clickAt(x, y, 900);
    await sleep(3800);
  });

  // Fiche d'un contact : clic, puis défilement de toute la fiche
  await take('5-contact', async () => {
    await sleep(300);
    const pt = await page.evaluate(() => {
      const all = __S.contacts(), n = (k, v) => all.filter(c => c[k] === v).length;
      const vis = __S.nodes().selectAll('circle.contact').nodes().filter(el => getComputedStyle(el).opacity > .5);
      const el = vis.sort((a, b) => (n('company', b.__data__.c.company) * 10 + n('school', b.__data__.c.school)) - (n('company', a.__data__.c.company) * 10 + n('school', a.__data__.c.school)))[0];
      const r = el.getBoundingClientRect();
      return [r.x + r.width / 2, r.y + r.height / 2];
    });
    await clickAt(pt[0], pt[1], 900);
    await sleep(2600);
    await move(1460, 560, 700);
    for (let i = 0; i < 12; i++) { await page.mouse.wheel(0, 70); await sleep(110); }
    await sleep(1600);
    for (let i = 0; i < 10; i++) { await page.mouse.wheel(0, 70); await sleep(110); }
    await sleep(2200);
  });

  // Filtres de séniorité
  await setup();
  await take('6-filtres', async () => {
    await page.evaluate(() => document.querySelector('#f-seniority').scrollIntoView({ block: 'center' }));
    await sleep(500);
    for (const v of ['Junior', 'Senior']) {
      const [x, y] = await centerOf(page.locator(`#f-seniority button[data-v="${v}"]`));
      await clickAt(x, y, 700);
      await sleep(1400);
    }
    await sleep(1000);
  });

  // Regrouper par entreprise, puis Branches affichées : de 5 à toutes
  await setup();
  await take('7-entreprises', async () => {
    await pickFrom('groupBy', 'company');
    await sleep(2600);
    const box = await page.locator('#topN').boundingBox();
    const at = v => box.x + 9 + (box.width - 18) * (v - 3) / 37;
    const y = box.y + box.height / 2;
    await move(at(12), y, 700); await sleep(150); await page.mouse.down();
    await move(at(5), y, 900); await sleep(1100);
    await move(at(40), y, 1800); await page.mouse.up(); cur = { x: at(40), y };
    await sleep(2600);
  });

  // Import : une archive .zip fictive (les contacts de démo au format LinkedIn, profil « Alex Martin ») glissée sur la page, puis lâchée.
  // Filmé en dernier, car l'import remplace le réseau de démo. Supabase est bloqué : le compteur public ne bouge pas.
  if (!only.length || only.includes('1-import')) {
    await page.evaluate(() => {
      const M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      const q = v => /[",]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : (v || '');
      const rows = __S.demoContacts().map(c => {
        const [f, ...l] = c.name.split(' '); const d = c.date ? new Date(c.date) : null;
        return [f, l.join(' '), '', '', c.company, c.position, d ? `${String(d.getDate()).padStart(2, '0')} ${M[d.getMonth()]} ${d.getFullYear()}` : ''].map(q).join(',');
      });
      const csv = 'Notes:\n"When exporting your connection data, you may notice that some of the email addresses are missing."\n\nFirst Name,Last Name,URL,Email Address,Company,Position,Connected On\n' + rows.join('\n') + '\n';
      const zip = new JSZip(); zip.file('Connections.csv', csv);
      zip.file('Profile.csv', 'First Name,Last Name,Maiden Name,Address,Birth Date,Headline,Summary,Industry,Zip Code,Geo Location,Twitter Handles,Websites,Instant Messengers\nAlex,Martin,,,,Product Manager,,Technology,,"Paris, France",,,\n');
      window.__zip = zip.generateAsync({ type: 'blob' }).then(b => new File([b], 'Basic_LinkedInDataExport.zip', { type: 'application/zip' }));
      /* Départ : le réseau de démonstration, avec son bandeau, comme à la première visite */
      __S.unhide(); __S.load(__S.demoContacts(), true);
      const g = document.createElement('div'); g.id = '__drag';
      g.innerHTML = '<i style="flex:none;width:34px;height:40px;border-radius:7px;background:#2F5BEA;color:#fff;font:800 10px/40px system-ui;text-align:center;font-style:normal">ZIP</i><span>Basic_LinkedInDataExport.zip</span>';
      Object.assign(g.style, { position:'fixed', zIndex:2147483640, pointerEvents:'none', display:'none', alignItems:'center', gap:'10px', padding:'10px 14px', background:'#fff', borderRadius:'12px', boxShadow:'0 14px 34px rgba(0,0,0,.2)', font:'700 14px system-ui', transform:'translate(14px,14px) rotate(-3deg)' });
      document.body.appendChild(g);
      addEventListener('mousemove', e => { g.style.left = e.clientX + 'px'; g.style.top = e.clientY + 'px'; }, true);
    });
    await sleep(1500);
    await take('1-import', async () => {
      await move(140, 900, 10);
      await sleep(900);
      await page.evaluate(() => { document.getElementById('__drag').style.display = 'flex'; });
      await move(500, 700, 700);
      await page.evaluate(async () => {
        const dt = new DataTransfer(); dt.items.add(await window.__zip); window.__dt = dt;
        window.dispatchEvent(new DragEvent('dragenter', { dataTransfer: dt, bubbles: true }));
      });
      await move(800, 520, 800);
      await sleep(700);
      await page.evaluate(() => {
        document.getElementById('__drag').style.display = 'none';
        window.dispatchEvent(new DragEvent('drop', { dataTransfer: window.__dt, bubbles: true, cancelable: true }));
      });
      await sleep(600);
      await move(1100, 860, 900);
      await sleep(3200);
    });
  }

  // Image de couverture : le graphe seul (sans légende ni boutons), recentré
  if (!only.length || only.includes('cover')) {
    await setup();
    await page.addStyleTag({ content: '#legend,#canvas .zoomctl,#canvas .toprow,#canvas button,#__cur{visibility:hidden!important}' });
    await page.evaluate(() => document.getElementById('recenter').click());
    await sleep(1500);
    await page.locator('#canvas').screenshot({ path: path.join(CLIPS, 'graphe.png') });
    console.log('cover ok');
  }

  await browser.close();
  fs.rmSync(TMP, { recursive: true, force: true });
})().catch(e => { console.error(e); process.exit(1); });
