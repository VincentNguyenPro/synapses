// Génère la voix off avec ElevenLabs, phrase par phrase, calée sur le minutage de script-voix-off.md.
// Seul le texte du script part chez ElevenLabs. La clé est lue dans ELEVENLABS_API_KEY, ou dans
// ~/.config/synapses/elevenlabs.env (ELEVENLABS_API_KEY=…) : jamais dans le dépôt.
// Usage : node video/voix-ia.js [nom de la voix, « Max » par défaut]   → video/out/voix-ia.m4a
const fs = require('fs'), os = require('os'), path = require('path');
const { execFileSync } = require('child_process');

let KEY = process.env.ELEVENLABS_API_KEY;
const ENV = path.join(os.homedir(), '.config', 'synapses', 'elevenlabs.env');
if (!KEY && fs.existsSync(ENV)) KEY = (fs.readFileSync(ENV, 'utf8').match(/ELEVENLABS_API_KEY=(\S+)/) || [])[1];
if (!KEY) { console.error(`Clé ElevenLabs introuvable : définis ELEVENLABS_API_KEY ou crée ${ENV}.`); process.exit(1); }
const VOICE_NAME = process.argv[2] || 'Max';
const OUT = path.join(__dirname, 'out', 'voix-ia.m4a');
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'synapses-voix-'));
const API = 'https://api.elevenlabs.io/v1';
const H = { 'xi-api-key': KEY, 'Content-Type': 'application/json' };

/* Ton d’une vidéo de lancement YC : un fondateur qui présente son produit, énergique mais naturel.
   Eleven v3 lit les indications entre crochets ; Multilingual v2, en repli, se règle par style et stabilité. */
const MODELS = [
  { id: 'eleven_v3', tag: true, settings: { stability: 0.5 } },
  { id: 'eleven_multilingual_v2', tag: false, settings: { stability: 0.32, similarity_boost: 0.8, style: 0.65, use_speaker_boost: true } }
];
const TAG = '[enthusiastic] ';

const sec = s => { const [m, r] = s.split(':'); return +m * 60 + parseFloat(r.replace(',', '.')); };
const rows = fs.readFileSync(path.join(__dirname, 'script-voix-off.md'), 'utf8').split('\n')
  .map(l => l.match(/^\| (\d:\d\d,\d) \| (\d:\d\d,\d) \| [^|]* \| (.*) \|\s*$/))
  .filter(m => m && !m[3].includes('silence'))
  .map(m => ({ a: sec(m[1]), b: sec(m[2]), text: m[3] }));
const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]));

async function speak(voiceId, model, text, f, prev, next) {
  const res = await fetch(`${API}/text-to-speech/${voiceId}?output_format=mp3_44100_128`, {
    method: 'POST', headers: H,
    body: JSON.stringify({ text: (model.tag ? TAG : '') + text, model_id: model.id, language_code: 'fr', voice_settings: model.settings,
      ...(model.tag ? {} : { previous_text: prev, next_text: next }) })
  });
  if (!res.ok) return `${res.status} ${(await res.text()).slice(0, 200)}`;
  fs.writeFileSync(f, Buffer.from(await res.arrayBuffer()));
  return '';
}

(async () => {
  /* La voix choisie, parmi « Mes voix » */
  const vr = await fetch(`${API}/voices`, { headers: H });
  if (!vr.ok) { console.error(`ElevenLabs refuse la liste des voix (${vr.status}) : vérifie la clé et ses droits « Voices ».`); process.exit(1); }
  const voice = (await vr.json()).voices.find(v => v.name.toLowerCase().startsWith(VOICE_NAME.toLowerCase()));
  if (!voice) { console.error(`Voix « ${VOICE_NAME} » absente de « Mes voix » : ajoute-la depuis la bibliothèque.`); process.exit(1); }
  console.log(`Voix : ${voice.name}`);

  let model = MODELS[0];
  const inputs = [], filt = [];
  for (const [i, r] of rows.entries()) {
    const f = path.join(TMP, `l${String(i).padStart(2, '0')}.mp3`);
    let err = await speak(voice.voice_id, model, r.text, f, rows[i - 1]?.text, rows[i + 1]?.text);
    if (err && model === MODELS[0]) { console.log(`Eleven v3 indisponible (${err}) : repli sur Multilingual v2`); model = MODELS[1]; err = await speak(voice.voice_id, model, r.text, f, rows[i - 1]?.text, rows[i + 1]?.text); }
    if (err) { console.error(`Erreur ElevenLabs : ${err}`); process.exit(1); }
    /* Une phrase plus longue que sa scène est légèrement accélérée (au plus × 1,25) */
    const d = dur(f), tempo = Math.min(1.25, Math.max(1, d / (r.b - r.a - 0.3)));
    console.log(`${String(i).padStart(2)}  ${r.a.toFixed(1).padStart(5)} s  scène ${(r.b - r.a).toFixed(1)} s  voix ${d.toFixed(1)} s${tempo > 1 ? `  accélérée × ${tempo.toFixed(2)}` : ''}`);
    const ms = Math.round((r.a + 0.15) * 1000);
    inputs.push('-i', f);
    filt.push(`[${i}:a]atempo=${tempo.toFixed(3)},adelay=${ms}|${ms}[v${i}]`);
  }
  filt.push(rows.map((_, i) => `[v${i}]`).join('') + `amix=inputs=${rows.length}:normalize=0,loudnorm=I=-16:TP=-1.5[o]`);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', filt.join(';'), '-map', '[o]', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', OUT]);
  fs.rmSync(TMP, { recursive: true, force: true });
  console.log(`→ ${OUT} (modèle ${model.id})`);
})().catch(e => { console.error(e); process.exit(1); });
