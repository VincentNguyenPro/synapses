"""Compose la musique du film de lancement (film-yc.html), calée sur script-yc.md.

Style « piano spatial » des films de science-fiction : piano qui répète une figure obstinée, cordes qui s’épaississent,
basse grave, gros tambours, grande salle. Un style n’est pas protégé ; la figure, les accords et la mélodie sont écrits ici et
ne reprennent aucun morceau existant (ni Interstellar ni autre musique de film : droits d’auteur).
Tout est synthétisé, sans échantillon : aucun droit à gérer.
  - ouverture : une octave grave au piano, les cordes s’installent ;
  - le problème : deux notes de piano qui se répondent, de plus en plus serrées, une montée de cymbale ;
  - le logo : grand accord grave, impact, les cordes s’ouvrent ;
  - les plans de l’app : ostinato en doubles croches, mélodie lente doublée par les violons, tambours, crescendo ;
  - la confidentialité : piano seul ;
  - la fin : grand accord de ré majeur, piano et cordes, quelques notes aiguës qui s’éteignent.
Usage : python3 video/musique-yc.py   → video/out/musique-yc.wav
"""
import os, re, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 110
SPB = 60 / BPM
rng = np.random.default_rng(5)

# ---------- Minutage : lu dans script-yc.md ----------
def sec(s):
    m, r = s.split(':'); return int(m) * 60 + float(r.replace(',', '.'))
rows = [re.match(r'^\| (\d:\d\d,\d) \| (\d:\d\d,\d) \| ([^|]*) \|', l) for l in open(os.path.join(HERE, 'script-yc.md'), encoding='utf-8')]
rows = [(sec(m.group(1)), sec(m.group(2)), m.group(3)) for m in rows if m]
T = [a for a, _, _ in rows]
END = rows[-1][1]
iL = next(i for i, r in enumerate(rows) if 'Logo' in r[2])
iP = next(i for i, r in enumerate(rows) if re.match(r'\s*1\.', r[2]))
iC = next(i for i, r in enumerate(rows) if 'Cadenas' in r[2])
LOGO, PROD, SHOTS, PRIV, FIN = T[iL], T[iP], T[iP:iC], T[iC], T[-1]
N = int(END * SR) + 2 * SR
dry = np.zeros((N, 2)); wet = np.zeros((N, 2))

# ---------- Outils ----------
def lp(x, f):  return sosfilt(butter(2, min(f, SR / 2.2) / (SR / 2), 'low', output='sos'), x)
def hp(x, f):  return sosfilt(butter(2, f / (SR / 2), 'high', output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo / (SR / 2), min(hi, SR / 2.2) / (SR / 2)], 'band', output='sos'), x)
def hz(n):     return 440 * 2 ** ((n - 69) / 12)
def tt(d):     return np.arange(int(d * SR)) / SR
def add(sig, t, gain=1.0, pan=0.0, rev=.5):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig[max(0, -i):max(0, min(len(sig), N - i))]; i = max(i, 0)
    l, r = s * gain * (1 - max(0, pan)), s * gain * (1 + min(0, pan))
    dry[i:i + len(s), 0] += l; dry[i:i + len(s), 1] += r
    wet[i:i + len(s), 0] += l * rev; wet[i:i + len(s), 1] += r * rev
def env(t, d, att, rel):
    e = np.minimum(1, t / max(att, 1e-4)); n = int(d * SR)
    e[n:] *= np.exp(-(t[n:] - d) / max(rel / 3, 1e-3))
    return e

# ---------- Piano : synthèse additive, cordes légèrement désaccordées, harmoniques inharmoniques ----------
def piano(note, d=None, vel=.7):
    f0 = hz(note)
    t60 = float(np.interp(note, [21, 60, 108], [9, 5, 1.2]))           # les graves résonnent plus longtemps (pédale)
    if d: t60 = min(t60, d + .4)
    L = tt(t60 + .3); x = np.zeros_like(L)
    B = .00012 * 2 ** ((note - 21) / 24)                              # inharmonicité de la corde
    nh = int(min(24, 9000 / f0))
    for h in range(1, nh + 1):
        fh = f0 * h * np.sqrt(1 + B * h * h)
        a = (1 / h ** (1.2 - .5 * vel)) * (1 if h != 7 else .3)        # le marteau frappe au 1/7 : peu de 7e harmonique
        dec = t60 / (1 + .35 * (h - 1)) / 6.9
        for cents in ((-.9, .9) if note > 40 else (0,)):               # deux cordes par note, qui battent doucement
            x += a * np.sin(2 * np.pi * fh * 2 ** (cents / 1200) * L + rng.random() * 6.28) * (np.exp(-L / dec) * .75 + np.exp(-L / (dec * 4)) * .25)
    x += lp(rng.standard_normal(len(L)), 1800 + 2500 * vel) * np.exp(-L / .012) * .6 * vel   # le marteau
    x *= np.minimum(1, L / .002)
    if d:
        i = int((d + .3) * SR)
        x[i:] *= np.exp(-(L[i:] - d - .3) / .08)                       # étouffoir
    return x * vel * .09
def keys(notes, t, vel=.7, gain=1.0, rev=.55, d=None):
    for n in notes:
        add(piano(n, d, vel), t + rng.random() * .012, gain, pan=float(np.clip((n - 60) / 40, -.6, .6)), rev=rev)

# ---------- Cordes (ensemble) ----------
def strings(notes, d, att=1.0, rel=1.2, bright=2200):
    t = tt(d + rel); x = np.zeros_like(t)
    for n in notes:
        for v in range(5):
            f = hz(n) * 2 ** (rng.normal(0, 7) / 1200)
            vib = 1 + .0035 * np.sin(2 * np.pi * (5 + rng.random()) * t + rng.random() * 6)
            x += 2 * ((np.cumsum(f * vib) / SR + rng.random()) % 1) - 1
    y = lp(lp(x, bright), bright * 1.4) + bp(x, 2500, 4500) * .08
    return y * env(t, d, att, rel) * .035 / max(1, len(notes) ** .5)
def sub(note, d, att=.5, rel=1.0):
    t = tt(d + rel); return np.sin(2 * np.pi * hz(note) * t) * env(t, d, att, rel) * .35

# ---------- Percussions ----------
def drum(gain=1.0, low=48):
    """Gros tambour (type taiko) : peau grave qui chute, puis le corps."""
    t = tt(1.6)
    body = np.sin(2 * np.pi * np.cumsum(low + 90 * np.exp(-t / .03)) / SR) * np.exp(-t / .45)
    skin = lp(rng.standard_normal(len(t)), 900) * np.exp(-t / .04) * .6
    return np.tanh((body + skin) * 1.6) * .55 * gain
def boom(d=3.5):
    t = tt(d)
    return np.sin(2 * np.pi * np.cumsum(26 + 60 * np.exp(-t / .1)) / SR) * np.exp(-t / 1.2) * .9
def cymbal_swell(d):
    n = int(d * SR); x = hp(rng.standard_normal(n), 5000)
    return lp(x, 11000) * np.linspace(0, 1, n) ** 4 * .06
def timpani(note, d=2.2):
    t = tt(d); f = hz(note)
    x = np.sin(2 * np.pi * f * t * (1 + .03 * np.exp(-t / .05))) + .45 * np.sin(2 * np.pi * f * 1.51 * t) * np.exp(-t / .5)
    return (x * np.exp(-t / .9) + lp(rng.standard_normal(len(t)), 500) * np.exp(-t / .04) * .4) * .6

# ---------- Harmonie (écrite pour ce film) ----------
PROG = [[50, 53, 57, 62], [46, 50, 53, 58], [43, 50, 53, 57], [45, 50, 52, 57]]   # ré m – si♭ – sol m – la sus4
BASS = [38, 34, 31, 33]
BAR = 4 * SPB
ARP = [0, 2, 1, 3, 2, 1, 3, 2]
MELO = [(74, 4), (72, 2), (77, 2), (76, 6), (74, 2), (69, 4), (70, 2), (72, 2), (74, 8)]
def chord_at(t): return int(max(0, t - LOGO) // (2 * BAR)) % 4

# ---------- Composition ----------
# Ouverture : une octave grave au piano, les cordes s’installent
keys([26, 38], 0.05, .9, 1.1); add(timpani(26, 3), .05, .6, rev=.5)
add(strings([38, 45, 50], LOGO - 1.5, att=3.0, rel=1.5, bright=1200), .5, .9, rev=.6)
add(sub(26, LOGO - .8, att=2.0), 0, .8, rev=.1)
# Le problème : deux notes de piano qui se répondent, de plus en plus serrées
t = T[1]; i = 0
FIG = [[62, 69], [62, 69], [62, 70], [62, 70]]                       # ré–la puis ré–si♭ : écrit pour ce film
while t < LOGO - .5:
    k = (t - T[1]) / (LOGO - T[1])
    pair = FIG[int((t - T[1]) // (2 * BAR)) % 4]
    keys([pair[i % 2] + (12 if k > .55 and i % 4 == 3 else 0)], t, .35 + .35 * k, .9, rev=.6, d=SPB * .9)
    t += SPB / 2 if k < .5 else SPB / 4; i += 1
add(cymbal_swell(3.0), LOGO - 3.05, .9, rev=.5)
for j, tb in enumerate(np.arange(LOGO - BAR / 2, LOGO - .2, SPB / 2)):
    add(drum(.35 + .3 * j / 4, 52), tb, 1.0, rev=.3)
# Logo : grand accord grave, impact, les cordes s’ouvrent
keys([26, 38, 45, 50, 57, 62], LOGO, 1.0, 1.2, rev=.6)
add(boom(), LOGO, 1.0, rev=.3); add(drum(1.2, 44), LOGO, 1.0, rev=.4)
add(strings([50, 57, 62, 65], 3.0, att=.08, rel=1.5, bright=3200), LOGO, 1.0, rev=.6)

# Ostinato de piano : croches sous le logo, doubles croches sur les plans de l’app
t = LOGO + BAR / 2; i = 0
while t < PRIV - .3:
    c = PROG[chord_at(t)]
    k = min(1, max(0, (t - LOGO) / (PRIV - LOGO)))
    step = SPB / 2 if t < PROD else SPB / 4
    keys([c[ARP[i % 8]] + 12], t, .4 + .4 * k, .8 + .3 * k, rev=.5, d=step * 1.6)
    t += step; i += 1
# Basse, accords de piano, cordes : à chaque changement d’harmonie, de plus en plus pleins
t = LOGO + BAR / 2
while t < PRIV - .3:
    j = chord_at(t); d = min(2 * BAR, PRIV - .3 - t)
    k = (t - LOGO) / (PRIV - LOGO)
    keys([BASS[j] - 12, BASS[j]], t, .6 + .35 * k, 1.0, rev=.5)
    add(sub(BASS[j] - 12, d, att=.1), t, .6 + .4 * k, rev=.1)
    add(strings(PROG[j][:3] + ([PROG[j][0] + 12] if k > .5 else []), d, att=.6, rel=1.0, bright=1800 + 2200 * k), t, .5 + .8 * k, rev=.6)
    if k > .55: add(strings([BASS[j]], d, att=.4, rel=1.0, bright=900), t, .8, rev=.4)   # violoncelles
    t += 2 * BAR
# Mélodie lente, aiguë, au piano, doublée par les violons quand ça monte
t = PROD + 2 * BAR
for note, beats in MELO * 2:
    if t >= PRIV - 1: break
    d = min(beats * SPB, PRIV - .6 - t)
    k = (t - PROD) / (PRIV - PROD)
    keys([note, note + 12] if k > .5 else [note], t, .75, .9, rev=.6)
    if k > .4: add(strings([note], d, att=.25, rel=.8, bright=3500), t, .7, rev=.6)
    t += beats * SPB
# Tambours : un coup par mesure, puis deux, puis quatre ; une timbale à chaque plan
t = PROD
while t < PRIV - .4:
    k = (t - PROD) / (PRIV - PROD)
    add(drum(.5 + .6 * k, 48), t, 1.0, rev=.35)
    t += BAR if k < .35 else (BAR / 2 if k < .7 else SPB)
for s_ in SHOTS:
    add(timpani(BASS[chord_at(s_)] - 12, 2.0), s_, .6, rev=.5)
add(cymbal_swell(2.2), PRIV - 2.25, 1.0, rev=.5)

# Confidentialité : piano seul, doux
keys([38, 50, 57, 62], PRIV + .05, .45, .9, rev=.7)
t = PRIV + BAR / 2; i = 0
while t < FIN - .5:
    keys([[69, 74][i % 2]], t, .3, .8, rev=.7, d=SPB); t += SPB; i += 1
add(strings([50, 57], FIN - PRIV, att=1.0, rel=1.0, bright=1100), PRIV, .6, rev=.6)
add(cymbal_swell(1.6), FIN - 1.65, 1.0, rev=.5)
for j, tb in enumerate(np.arange(FIN - BAR / 2, FIN - .1, SPB / 4)):
    add(drum(.3 + .5 * j / 8, 52), tb, 1.0, rev=.3)
# Fin : ré majeur, piano, cordes, tambours
keys([26, 38, 45, 50, 54, 57, 62, 66], FIN, 1.0, 1.2, rev=.65)
add(strings([38, 45, 50, 54, 57, 62, 66], END - FIN - .8, att=.1, rel=2.0, bright=3000), FIN, 1.2, rev=.65)
add(sub(26, END - FIN - .5, att=.05, rel=1.5), FIN, .9, rev=.1)
add(boom(4), FIN, 1.0, rev=.4); add(drum(1.3, 44), FIN, 1.0, rev=.5); add(timpani(26, 3.5), FIN, .8, rev=.5)
for j, n in enumerate([74, 78, 81, 86, 81, 78]):
    keys([n], FIN + 1.2 + j * SPB, .4 - .04 * j, .8, rev=.75)

# ---------- Réverbération (grande salle de concert) et mixage ----------
L = int(4.5 * SR); tr = np.arange(L) / SR
ir = []
for c in range(2):
    x = hp(rng.standard_normal(L), 90) * np.exp(-tr / .95)
    x = lp(x, 5000) * .5 + lp(x, 1500) * .5                    # les aigus s’éteignent plus vite
    x[:int(.03 * SR)] = 0                                       # pré-délai
    for d, g in ((.051, .5), (.073, .4), (.097, .35), (.131, .3)):   # premières réflexions
        x[int((d + c * .007) * SR)] += g * 40
    ir.append(x)
rev = np.stack([fftconvolve(wet[:, c], ir[c])[:N] for c in range(2)], axis=1)
out = dry + rev / np.max(np.abs(rev)) * np.max(np.abs(dry)) * .5
out = out[:int(END * SR)]
f = int(1.2 * SR); out[-f:] *= np.linspace(1, 0, f)[:, None]
out = np.tanh(out / np.max(np.abs(out)) * 1.25) / np.tanh(1.25) * .9
pcm = (out * 32767).astype(np.int16)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
with wave.open(os.path.join(HERE, 'out', 'musique-yc.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'→ video/out/musique-yc.wav ({END:.1f} s, {BPM} BPM, accord du logo à {LOGO:.1f} s)')
