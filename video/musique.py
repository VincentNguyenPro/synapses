"""Compose la musique de fond de la vidéo, calée sur les scènes de script-voix-off.md.

Tout est synthétisé ici (aucun échantillon externe, donc aucun droit à gérer) :
  - le problème (liste, questions) : nappes en la mineur, basse pulsée, tension qui monte ;
  - le logo : impact, puis le beat arrive (progression lumineuse do – sol – la mineur – fa) ;
  - les fonctions : groove continu, arpège en plus, un souffle et un impact à chaque nouvelle étape ;
  - la confidentialité : respiration, nappes seules ; la fin : accord final qui s’éteint.
Usage : python3 video/musique.py   → video/out/musique.wav
"""
import os, re, wave
import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 118
SPB = 60 / BPM                      # durée d’un temps
rng = np.random.default_rng(7)

# ---------- Minutage : début de chaque ligne du script, dans l’ordre ----------
def sec(s):
    m, r = s.split(':'); return int(m) * 60 + float(r.replace(',', '.'))
rows = [re.match(r'^\| (\d:\d\d,\d) \| (\d:\d\d,\d) \|', l) for l in open(os.path.join(HERE, 'script-voix-off.md'), encoding='utf-8')]
rows = [(sec(m.group(1)), sec(m.group(2))) for m in rows if m]
T = [a for a, _ in rows]
END = rows[-1][1]
LOGO, PROD, SHOTS, PRIV, FIN = T[4], T[7], T[7:-2], T[-2], T[-1]   # plans de l’app : de « Dépose l’archive » au cadenas
N = int(END * SR) + SR
out = np.zeros((N, 2))

# ---------- Outils ----------
def lp(x, f):  return sosfilt(butter(2, f / (SR / 2), 'low', output='sos'), x)
def hp(x, f):  return sosfilt(butter(2, f / (SR / 2), 'high', output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos'), x)
def hz(n):     return 440 * 2 ** ((n - 69) / 12)        # numéro MIDI → fréquence
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig[max(0, -i):max(0, min(len(sig), N - i))]
    i = max(i, 0)
    out[i:i + len(s), 0] += s * gain * (1 - max(0, pan))
    out[i:i + len(s), 1] += s * gain * (1 + min(0, pan))
def env(n, a, d):  # attaque linéaire puis décroissance exponentielle, en secondes
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def saw(f, dur):
    t = np.arange(int(dur * SR)) / SR
    return 2 * ((t * f) % 1) - 1

# ---------- Instruments ----------
def kick():
    n = int(.42 * SR); t = np.arange(n) / SR
    f = 46 + 110 * np.exp(-t / .045)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .16) + .3 * hp(rng.standard_normal(n), 3000) * np.exp(-t / .004)
def clap():
    n = int(.25 * SR); x = bp(rng.standard_normal(n), 900, 5000)
    e = np.exp(-np.arange(n) / SR / .07)
    for k in (0, .011, .022): e[int(k * SR):int(k * SR) + 200] += .8
    return x * e * .5
def hat(open_=False):
    n = int((.22 if open_ else .05) * SR)
    return lp(hp(rng.standard_normal(n), 7000), 12000) * np.exp(-np.arange(n) / SR / (.06 if open_ else .012)) * .22
def bass(note, dur):
    f = hz(note); x = saw(f, dur) + .5 * np.sin(2 * np.pi * f / 2 * np.arange(int(dur * SR)) / SR)
    return lp(x, 380) * env(len(x), .005, dur * .9) * .55
def pluck(note, dur=.22):
    x = saw(hz(note), dur) + saw(hz(note) * 1.004, dur)
    return lp(x, 2600) * env(len(x), .002, .09) * .16
def pad(notes, dur, bright=1400):
    x = sum(saw(hz(n) * d, dur) for n in notes for d in (0.997, 1.003))
    n = len(x); a = int(min(.6, dur / 3) * SR)
    e = np.ones(n); e[:a] = np.linspace(0, 1, a); e[-a:] *= np.linspace(1, 0, a)
    return lp(x, bright) * e * .05
def whoosh(dur=.6):  # souffle qui monte vers un impact
    n = int(dur * SR); x = rng.standard_normal(n)
    y = np.concatenate([bp(x[i:i + 2205], 300 + 6000 * (i / n) ** 2, 1200 + 9000 * (i / n) ** 2) for i in range(0, n, 2205)])[:n]
    return y * np.linspace(0, 1, n) ** 2 * .35
def impact():
    n = int(1.6 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t / .08)) / SR) * np.exp(-t / .5)
    crash = hp(rng.standard_normal(n), 4000) * np.exp(-t / .45) * .25
    return boom * .8 + crash
def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR) * .08
    return (tone + whoosh(dur) * .6) * (t / dur) ** 1.5

# ---------- Harmonie ----------
MINOR = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]        # la m – fa – do – sol
BRIGHT = [[48, 52, 55, 59], [55, 59, 62], [57, 60, 64], [53, 57, 60, 64]]  # do – sol – la m – fa
BAR = 4 * SPB

def section_pads(t0, t1, prog, bright, gain=1.0):
    t, k = t0, 0
    while t < t1:
        d = min(BAR * 2, t1 - t)
        add(pad(prog[k % 4], d + .4, bright), t, gain, pan=-.2)
        add(pad([n + 12 for n in prog[k % 4][:2]], d + .4, bright), t, gain * .6, pan=.25)
        t += BAR * 2; k += 1

def groove(t0, t1, prog, arp=False, hats=True, claps=True, kick_gain=1.0):
    """Beat calé sur la grille qui part du logo : les temps tombent juste quelle que soit la scène."""
    k0 = int(np.ceil((t0 - LOGO) / SPB - 1e-6))
    t = LOGO + k0 * SPB; i = k0
    while t < t1 - 1e-6:
        chord = prog[(i // 8) % 4]
        add(kick(), t, .9 * kick_gain)
        if claps and i % 2 == 1: add(clap(), t, .5, pan=.05)
        if hats: add(hat(True), t + SPB / 2, .55, pan=.3)
        if hats: add(hat(), t + SPB / 4, .35, pan=-.3); add(hat(), t + 3 * SPB / 4, .3, pan=-.3)
        add(bass(chord[0] - 24, SPB / 2 - .02), t + SPB / 2, 1.0)
        add(bass(chord[0] - 24, SPB / 2 - .02), t, .8)
        if arp:
            for j in range(4):
                add(pluck(chord[j % len(chord)] + 12 + (12 if j == 3 else 0)), t + j * SPB / 4, 1, pan=(-.4 if j % 2 else .4))
        t += SPB; i += 1

# ---------- Composition ----------
# Couverture et problème : la mineur, sobre, avec une basse qui pulse
add(pad(MINOR[0], T[1] + .5, 900), 0, .8)
section_pads(T[1], LOGO, MINOR, 1100, .9)
t = T[1]; k = 0
while t < LOGO - .05:
    add(bass(MINOR[int((t - T[1]) // (BAR * 2)) % 4][0] - 24, SPB / 2 - .03), t, .45 + .3 * (t - T[1]) / (LOGO - T[1]))
    if t > T[3]: add(hat(), t, .25)                 # les questions : un peu plus de tension
    t += SPB / 2; k += 1
add(riser(LOGO - T[3] - 1.2), T[3] + 1.2, .9)

# Logo : impact, puis le beat
add(impact(), LOGO, 1.0)
section_pads(LOGO, PRIV, BRIGHT, 1800, .8)
groove(LOGO + BAR, PROD, BRIGHT, arp=False)
add(whoosh(.8), PROD - .8, .8)

# Les fonctions : groove complet, un souffle et un impact léger à chaque étape
groove(PROD, PRIV - SPB, BRIGHT, arp=True)
for s in SHOTS:
    add(whoosh(.45), s - .45, .6)
    add(impact()[:int(.7 * SR)] * np.linspace(1, 0, int(.7 * SR)), s, .35)
add(riser(2.0), PRIV - 2.0, .5)

# Confidentialité : respiration
add(impact(), PRIV, .6)
section_pads(PRIV, FIN, MINOR[2:] + MINOR[:2], 900, .9)
groove(PRIV, FIN - SPB, BRIGHT, hats=False, claps=False, kick_gain=.45)

# Fin : accord final qui s’éteint
add(impact(), FIN, .9)
add(pad(BRIGHT[0] + [64], END - FIN + .5, 2200), FIN, 1.2)
groove(FIN, FIN + 2 * BAR, BRIGHT, arp=True)

# ---------- Mixage final ----------
out = out[:int(END * SR)]
fade = int(1.2 * SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
out /= np.max(np.abs(out)) / 0.89
pcm = (out * 32767).astype(np.int16)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
with wave.open(os.path.join(HERE, 'out', 'musique.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'→ video/out/musique.wav ({END:.1f} s, {BPM} BPM, beat à partir de {LOGO:.1f} s)')
