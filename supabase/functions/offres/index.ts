// Synapses : recherche d’offres d’emploi pour « Offres d’emploi pour toi » (choix de Vincent du 13 novembre 2026)
// Fonction Supabase (Edge Function, Deno), projet afvmshbacxaznhmlgkzc, région UE.
//
// Reçoit seulement des critères de recherche : intitulé, lieu, années d’expérience, salaire minimum (k€ brut par an).
// Jamais un contact, jamais le réseau. Rien n’est gardé : la fonction interroge l’API officielle d’Adzuna
// (developer.adzuna.com, agrégateur d’offres de nombreux sites, France ou Suisse selon le lieu) et renvoie la liste.
// LinkedIn, Indeed, Hellowork et Welcome to the Jungle n’ont pas d’API publique : l’outil ouvre leurs recherches pré-remplies.
// France Travail : l’API « Offres d’emploi » n’est plus proposée dans le catalogue francetravail.io (novembre 2026).
//
// Secrets (Supabase › Edge Functions › Secrets, jamais dans ce dépôt public) : ADZUNA_APP_ID, ADZUNA_APP_KEY.
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
  let list: Offre[] = [], etat = env('ADZUNA_APP_ID') ? 'ok' : 'off';
  try { list = await adzuna(q, lieu, exp, sal); } catch { etat = 'erreur'; }
  const seen = new Set<string>();
  const offres = list.filter((o) => { const k = norm(o.t) + '|' + norm(o.n); if (!o.t || seen.has(k)) return false; seen.add(k); return true; })
    .sort((a, b) => b.d.localeCompare(a.d)).slice(0, 40);
  return json({ offres, sources: { Adzuna: etat } });
});
