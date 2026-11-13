// Synapses : recherche d’offres d’emploi pour « Offres d’emploi pour toi » (choix de Vincent du 13 novembre 2026)
// Fonction Supabase (Edge Function, Deno), projet afvmshbacxaznhmlgkzc, région UE.
//
// Reçoit seulement des critères de recherche : intitulé, lieu, années d’expérience, salaire minimum (k€ brut par an).
// Jamais un contact, jamais le réseau. Rien n’est gardé : la fonction interroge les API officielles de deux agrégateurs,
// Adzuna (developer.adzuna.com) et Jooble (jooble.org/api/about), France ou Suisse selon le lieu, fusionne les doublons
// et renvoie la liste.
// LinkedIn, Indeed, Hellowork et Welcome to the Jungle n’ont pas d’API publique : l’outil ouvre leurs recherches pré-remplies.
// France Travail : l’API « Offres d’emploi » n’est plus proposée dans le catalogue francetravail.io (novembre 2026).
//
// Secrets (Supabase › Edge Functions › Secrets, jamais dans ce dépôt public) : ADZUNA_APP_ID, ADZUNA_APP_KEY, JOOBLE_KEY.
// Une source sans sa clé est ignorée.
// Déploiement : Supabase › Edge Functions › nom « offres », coller ce fichier, décocher « Verify JWT »
// (la clé publishable n’est pas un JWT ; la fonction n’ouvre l’accès à aucune donnée).

const ORIGINS = ['https://vincentnguyenpro.github.io', 'http://127.0.0.1:8765', 'http://localhost:8765'];
const env = (k: string) => Deno.env.get(k) || '';

type Offre = { src: string; t: string; n: string; lieu: string; sal: string; d: string; u: string; desc: string; contrat: string };

const norm = (s: string) => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
const clip = (s: string, n: number) => (s || '').replace(/\s+/g, ' ').trim().slice(0, n);
const SUISSE = /suisse|switzerland|geneve|geneva|lausanne|zurich|bale|basel|berne|bern|neuchatel|fribourg|lugano/;
const CONTRAT: Record<string, string> = { permanent: 'CDI', contract: 'CDD / mission', full_time: 'temps plein', part_time: 'temps partiel' };

async function adzuna(q: string, lieu: string, exp: number, sal: number): Promise<Offre[]> {
  if (!env('ADZUNA_APP_ID') || !env('ADZUNA_APP_KEY')) return [];
  const pays = SUISSE.test(norm(lieu)) ? 'ch' : 'fr';
  const p = new URLSearchParams({ app_id: env('ADZUNA_APP_ID'), app_key: env('ADZUNA_APP_KEY'), what: q, results_per_page: '40', sort_by: 'date', 'content-type': 'application/json' });
  // Expérience : Adzuna n’a pas de filtre ; un profil expérimenté écarte les stages et alternances
  if (exp >= 3) p.set('what_exclude', 'stage stagiaire alternance alternant apprenti internship');
  // « Île-de-France et périphérie », « Genève et périphérie » : on garde le nom du lieu
  const where = lieu.replace(/\s+et\s+p[ée]riph[ée]rie$/i, '').trim();
  if (where && !/^(france|suisse|switzerland)$/i.test(where)) p.set('where', where);
  if (sal > 0) p.set('salary_min', String(Math.round(sal * 1000)));
  const r = await fetch(`https://api.adzuna.com/v1/api/jobs/${pays}/search/1?` + p);
  if (!r.ok) throw new Error('adzuna ' + r.status);
  const j = await r.json(), k = (v: number) => Math.round(v / 1000) + ' k';
  return (j.results || []).map((o: any) => ({
    src: 'Adzuna', t: clip(o.title, 140), n: clip(o.company?.display_name || '', 80), lieu: clip(o.location?.display_name || '', 80),
    // Montant sous 10 000 : un taux journalier ou une erreur, pas un salaire annuel ; on ne l’affiche pas
    sal: o.salary_min >= 10000 ? (o.salary_max && o.salary_max !== o.salary_min ? `${k(o.salary_min)} – ${k(o.salary_max)}` : k(o.salary_min)) + (pays === 'ch' ? ' CHF' : ' €') + (String(o.salary_is_predicted) === '1' ? ' (estimé)' : '') : '',
    d: (o.created || '').slice(0, 10), contrat: clip([o.contract_type, o.contract_time].filter(Boolean).map((c: string) => CONTRAT[c] || c).join(', '), 40),
    u: o.redirect_url || '', desc: clip(o.description || '', 4000),
  }));
}

// Doublons (y compris entre Adzuna et Jooble) : Adzuna reçoit souvent la même annonce de plusieurs sources, sous un autre nom d’entreprise (forum de recrutement,
// site relais, autre entité du groupe : « KPMG SA » / « KPMG France »). Même intitulé publié à moins de 15 jours d’écart =
// même offre si l’intitulé est précis (4 mots ou plus) ; un intitulé court (« Product Manager ») doit aussi avoir la même entreprise.
// On garde la version la plus utile : vraie entreprise plutôt qu’intermédiaire, puis avec salaire, puis la plus récente.
const RELAIS = /talents? handicap|forum|job-?room|jobteaser|hellowork|indeed|jooble|adzuna|meteojob|jobijoba|cadremploi|monster|glassdoor|jobted|talent\.com|france travail|pole emploi/;
// Intitulé comparé sans « H/F », « F/H », « (M/F/D) »… : « Chef de projet PMO F/H » = « Chef de projet PMO »
const words = (s: string) => norm(s).replace(/\b([hfm])\s*\/\s*([hfmw])(\s*\/\s*[xd])?\b/g, ' ').replace(/[^a-z0-9]+/g, ' ').trim();
function dedupe(list: Offre[]): Offre[] {
  const score = (o: Offre) => (RELAIS.test(norm(o.n)) || !o.n ? 0 : 4) + (o.sal ? 2 : 0) + (o.desc.length > 200 ? 1 : 0);
  const days = (a: string, b: string) => Math.abs(Date.parse(a) - Date.parse(b)) / 864e5;
  const out: Offre[] = [];
  for (const o of list) {
    if (!o.t) continue;
    const t = words(o.t), precis = t.split(' ').length >= 4, co = words(o.n).split(' ')[0];
    // Même entreprise : même offre jusqu’à 60 jours d’écart (republiée ailleurs plus tard) ; sinon 15 jours et intitulé précis
    const i = out.findIndex((x) => words(x.t) === t && (words(x.n).split(' ')[0] === co ? !(days(x.d, o.d) > 60) : precis && !(days(x.d, o.d) > 15)));
    if (i < 0) { out.push(o); continue; }
    const best = score(o) > score(out[i]) ? o : out[i], other = best === o ? out[i] : o;
    const src = [...new Set([...best.src.split(', '), ...other.src.split(', ')])].join(', ');
    out[i] = { ...best, src, sal: best.sal || other.sal, contrat: best.contrat || other.contrat, desc: best.desc.length >= other.desc.length ? best.desc : other.desc, d: best.d > other.d ? best.d : other.d };
  }
  return out;
}

// Jooble : POST https://{fr|ch}.jooble.org/api/{clé}, corps { keywords, location, salary, page }. Une clé par pays :
// demandée sur fr.jooble.org/api/about (JOOBLE_KEY) et ch.jooble.org/api/about (JOOBLE_KEY_CH, facultative).
// La clé de jooble.org (international) renvoie des offres des États-Unis (« Paris » = Paris, Texas) : ne pas l’utiliser.
const stripTags = (s: string) => (s || '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&#39;|&apos;/g, '’').replace(/&quot;/g, '"');
async function jooble(q: string, lieu: string, exp: number, sal: number): Promise<Offre[]> {
  const pays = SUISSE.test(norm(lieu)) ? 'ch' : 'fr', cle = env(pays === 'ch' ? 'JOOBLE_KEY_CH' : 'JOOBLE_KEY');
  if (!cle) return [];
  const where = lieu.replace(/\s+et\s+p[ée]riph[ée]rie$/i, '').trim();
  const body: Record<string, unknown> = { keywords: q, page: '1', ResultOnPage: '40' };
  body.location = where && !/^(france|suisse|switzerland)$/i.test(where) ? where : (pays === 'ch' ? 'Suisse' : 'France');
  if (sal > 0) body.salary = Math.round(sal * 1000);
  const r = await fetch(`https://${pays}.jooble.org/api/${cle}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error('jooble ' + r.status);
  const j = await r.json();
  const stage = /\b(stage|stagiaire|alternance|alternant|apprenti|internship)\b/;
  // Jooble renvoie parfois des offres sans rapport : on garde celles dont l’intitulé reprend au moins un mot du poste cherché
  const mots = words(q).split(' ').filter((w) => w.length > 2 && !/^(les|des|une|pour|and|the|chef|senior|junior)$/.test(w));
  const pertinent = (t: string) => !mots.length || mots.some((w) => words(t).split(' ').some((x) => x === w || (w.length > 4 && x.startsWith(w.slice(0, -1)))));
  return (j.jobs || []).filter((o: any) => !(exp >= 3 && stage.test(norm(o.title || ''))) && pertinent(stripTags(o.title || ''))).map((o: any) => ({
    src: 'Jooble', t: clip(stripTags(o.title), 140), n: clip(o.company || '', 80), lieu: clip(o.location || '', 80),
    sal: /[£$]/.test(o.salary || '') ? '' : clip(o.salary || '', 60), d: (o.updated || '').slice(0, 10), contrat: clip(o.type || '', 40),
    u: /^https?:\/\//.test(o.link || '') ? o.link : '', desc: clip(stripTags(o.snippet || ''), 4000),
  }));
}

Deno.serve(async (req) => {
  const origin = req.headers.get('origin') || '';
  const cors = { 'Access-Control-Allow-Origin': ORIGINS.includes(origin) ? origin : ORIGINS[0], 'Access-Control-Allow-Headers': 'apikey, authorization, content-type, x-client-info', 'Access-Control-Allow-Methods': 'POST, OPTIONS', Vary: 'Origin' };
  const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'POST seulement' }, 405);
  let b: any = {};
  try { b = await req.json(); } catch { return json({ error: 'JSON attendu' }, 400); }
  const q = clip(String(b.q || ''), 100), lieu = clip(String(b.lieu || ''), 80);
  const exp = Math.max(0, Math.min(50, Number(b.exp) || 0)), sal = Math.max(0, Math.min(500, Number(b.sal) || 0));
  if (q.length < 2) return json({ offres: [], sources: {} });
  const [az, jb] = await Promise.allSettled([adzuna(q, lieu, exp, sal), jooble(q, lieu, exp, sal)]);
  const sources = {
    Adzuna: az.status === 'rejected' ? 'erreur ' + String((az as PromiseRejectedResult).reason?.message || '').replace(/\D+/g, '') : env('ADZUNA_APP_ID') ? 'ok' : 'off',
    Jooble: jb.status === 'rejected' ? 'erreur ' + String((jb as PromiseRejectedResult).reason?.message || '').replace(/\D+/g, '') : env('JOOBLE_KEY') ? 'ok' : 'off',
  };
  const list = [...(az.status === 'fulfilled' ? az.value : []), ...(jb.status === 'fulfilled' ? jb.value : [])];
  const offres = dedupe(list).sort((a, b) => b.d.localeCompare(a.d)).slice(0, 60);
  return json({ offres, sources });
});
