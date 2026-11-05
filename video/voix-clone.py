"""Voix off avec la voix de Vincent, clonée en local par Chatterbox Multilingual (Resemble AI, licence MIT) : rien n’est envoyé.

Installation, une fois (hors du dépôt ; setuptools < 81 : le filigrane Perth en a besoin) :
  uv venv --python 3.11 ~/.local/share/synapses-voix
  VIRTUAL_ENV=~/.local/share/synapses-voix uv pip install chatterbox-tts "setuptools<81" faster-whisper
Le modèle (quelques Go) est téléchargé depuis Hugging Face au premier lancement.

Échantillon : 1 à 2 minutes de Vincent qui parle naturellement, pièce calme (video/voix-vincent.m4a, jamais commité).
Le français peut servir aussi pour l’anglais : le modèle transpose la voix d’une langue à l’autre.

Usage :
  ~/.local/share/synapses-voix/bin/python video/voix-clone.py voix-vincent.m4a [--en] [--script script-yc.md] [--out voix-yc.m4a]
  → video/out/voix-yc.m4a (voix-yc-en.m4a avec --en, lu dans le script « -en » s’il existe)
Chaque phrase est calée sur le début de sa scène ; une phrase trop longue est accélérée (au plus × 1,25).
Chaque phrase est retranscrite par Whisper (faster-whisper, en local) et refaite jusqu’à 4 fois si un mot est déformé.
Les phrases réussies sont gardées dans out/voix-yc-lignes/ : --lignes 5,7 ne refait que celles-là.
Chatterbox marque chaque fichier d’un filigrane audio inaudible (Perth).
"""
import os, re, subprocess, sys, tempfile
import torch, torchaudio

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
EN = '--en' in args
sample = next((a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] not in ('--script', '--out', '--lignes'))), None)
if not sample: sys.exit('Indique l’échantillon de voix : python video/voix-clone.py voix-vincent.m4a')
sample = sample if os.path.isabs(sample) else os.path.join(HERE, sample)
script = opt('--script', 'script-yc.md')
if EN and os.path.exists(os.path.join(HERE, script.replace('.md', '-en.md'))): script = script.replace('.md', '-en.md')
out = os.path.join(HERE, 'out', opt('--out', 'voix-yc-en.m4a' if EN else 'voix-yc.m4a'))

sec = lambda s: (lambda m, r: int(m) * 60 + float(r.replace(',', '.')))(*s.split(':'))
rows = [re.match(r'^\| (\d:\d\d,\d) \| (\d:\d\d,\d) \| [^|]* \| (.*) \|\s*$', l) for l in open(os.path.join(HERE, script), encoding='utf-8')]
rows = [(sec(m[1]), sec(m[2]), m[3]) for m in rows if m and 'silence' not in m[3]]

tmp = tempfile.mkdtemp(prefix='synapses-clone-')
# Échantillon : mono 24 kHz, silences de début et de fin retirés, 20 s au plus (le modèle n’en garde pas davantage)
ref = os.path.join(tmp, 'ref.wav')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', sample, '-af',
  'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm',
  '-ac', '1', '-ar', '24000', '-t', '20', ref], check=True)

from chatterbox.mtl_tts import ChatterboxMultilingualTTS
dev = 'mps' if torch.backends.mps.is_available() else 'cpu'
# Les poids sont enregistrés pour CUDA : on les charge sur l’appareil disponible
_load = torch.load
torch.load = lambda *a, **k: _load(*a, **{**k, 'map_location': torch.device(dev)})
model = ChatterboxMultilingualTTS.from_pretrained(device=torch.device(dev))
print(f'Modèle chargé ({dev})')

dur = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

# Vérification : chaque phrase est retranscrite (Whisper, en local) et refaite tant qu’elle ne correspond pas au texte
import difflib, unicodedata
from faster_whisper import WhisperModel
asr = WhisperModel('small', device='cpu', compute_type='int8')
def norm(s):
    s = unicodedata.normalize('NFD', s.lower().replace('’', "'")).encode('ascii', 'ignore').decode()
    s = re.sub(r"[^a-z0-9 ]+", " ", s.replace("synapses", "synapse").replace("essaie", "essai"))
    return ' '.join(s.split())
def score(f, text):
    heard = ' '.join(x.text for x in asr.transcribe(f, language='en' if EN else 'fr')[0])
    return difflib.SequenceMatcher(None, norm(heard).split(), norm(text).split()).ratio(), heard.strip()

# Les phrases déjà réussies sont gardées (out/<sortie>-lignes/) : --lignes 5,7 ne refait que celles-là
keep = os.path.join(os.path.dirname(out), os.path.splitext(os.path.basename(out))[0] + '-lignes')
os.makedirs(keep, exist_ok=True)
only = {int(x) for x in opt('--lignes', '').split(',') if x}
ins, flt = [], []
for i, (a, b, text) in enumerate(rows):
    f = os.path.join(keep, f'l{i:02d}.wav')
    if not os.path.exists(f) or not only or i in only:
        best = None
        for essai in range(4):
            torch.manual_seed(1000 * i + essai)
            wav = model.generate(text, language_id='en' if EN else 'fr', audio_prompt_path=ref, exaggeration=0.55, cfg_weight=0.45)
            g = os.path.join(tmp, f'l{i:02d}-{essai}.wav'); torchaudio.save(g, wav.cpu(), model.sr)
            sc, heard = score(g, text)
            if not best or sc > best[0]: best = (sc, g, heard)
            if sc >= .97: break
        os.replace(best[1], f)
        if best[0] < .97: print(f'   ⚠ phrase {i} : entendu « {best[2]} »')
    d = dur(f); tempo = min(1.25, max(1, d / (b - a - .3)))
    print(f'{i:2d} {a:5.1f} s  scène {b - a:.1f} s  voix {d:.1f} s' + (f'  accélérée × {tempo:.2f}' if tempo > 1.005 else ''))
    ms = int((a + .15) * 1000); ins += ['-i', f]
    flt.append(f'[{i}:a]atempo={tempo:.3f},adelay={ms}|{ms}[v{i}]')
flt.append(''.join(f'[v{i}]' for i in range(len(rows))) + f'amix=inputs={len(rows)}:normalize=0,loudnorm=I=-16:TP=-1.5[o]')
os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(flt), '-map', '[o]', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', out], check=True)
print('→', out)
