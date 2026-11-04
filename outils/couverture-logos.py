#!/usr/bin/env python3
"""Mesure la part des contacts d’un export LinkedIn dont l’entreprise aura un logo dans Synapses.

Usage : python3 -I outils/couverture-logos.py <export.zip | Connections.csv> [--manquants 40]

Seule la colonne « Company » est lue : aucun nom, URL ni email de contact n’est lu ni affiché.
Le calcul reprend la logique de app/index.html : groupes de data/entreprises.json (groupOf),
rattachement par début de nom (parentOf), écritures d’un même nom (spellKey), puis domaine officiel
de data/domaines.json (domainOf). Rien n’est envoyé nulle part.
"""
import csv, io, json, re, sys, unicodedata, zipfile
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    return ''.join(ch for ch in s if not unicodedata.combining(ch)).strip()


def nkey(s):
    return re.sub(r'\s+', ' ', re.sub(r"['’]", ' ', norm(s))).strip()


def js_re(motif):
    # Les motifs de data/entreprises.json sont écrits pour JavaScript ; ils sont compatibles avec re pour l’essentiel
    return re.compile(motif)


ENT = json.loads((RACINE / 'data/entreprises.json').read_text(encoding='utf-8'))
DOMS = json.loads((RACINE / 'data/domaines.json').read_text(encoding='utf-8'))['domaines']
GROUPS = [(g['nom'], js_re(g['motif'])) for g in ENT.get('groupes', [])]
PREFIX_STOP = set(ENT.get('premiers_mots_ignores', []))
NO_COMPANY_GROUPS = {'Indépendant', 'Non communiqué'}
NOT_A_COMPANY = re.compile(r"\b(independant\w*|freelance\w*|self[- ]?employed|auto[- ]?entrepreneur\w*|confidenti\w*|prive|private|stealth|en recherche|open to work|^retraite\w*|retired|etudiant\w*|student|top secret|none|aucune?)\b|^[^a-z0-9]*$")
LEGAL_END = re.compile(r' (s\.?a\.?s\.?u?|s\.?a\.?|s\.?e\.?|sarl|inc|ltd|llc|gmbh|ag|spa|bv|nv|plc|group|groupe)\.?$')


def group_of(name):
    k = nkey(name)
    if not k:
        return ''
    for g, rx in GROUPS:
        if rx.search(k):
            return g
    return ''


def spell_key(name):
    k = re.sub(r'\.(fr|com|io|co|net|org|eu)$', '', re.sub(r'\s*\|.*$', '', nkey(name))).strip()
    while True:
        prev = k
        k = LEGAL_END.sub('', k).strip()
        if k == prev or ' ' not in k:
            return k


def domain_of(name):
    k = nkey(name)
    if not k or NOT_A_COMPANY.search(k):
        return ''
    no_tld = re.sub(r'\.(fr|com|io|co|net|org|ai|eu|ch|be|ca)$', '', k)
    no_lead = re.sub(r' (groupe|group|sa|sas|se)$', '', re.sub(r'^(le groupe|groupe|group|the) ', '', no_tld))
    parts = [x.strip() for x in re.split(r' [-|–—:] | ?[()]', no_lead) if x and x.strip()]
    for t in dict.fromkeys([k, no_tld, no_lead, *parts]):
        if t in DOMS:
            return DOMS[t]
        w = t.split(' ')
        for n in range(len(w) - 1, 0, -1):
            pre = ' '.join(w[:n])
            if n == 1 and pre in PREFIX_STOP:
                continue
            if pre in DOMS:
                return DOMS[pre]
    return ''


def read_companies(path):
    p = Path(path)
    if p.suffix.lower() == '.zip':
        with zipfile.ZipFile(p) as z:
            nom = next(n for n in z.namelist() if n.lower().endswith('connections.csv'))
            text = z.read(nom).decode('utf-8-sig')
    else:
        text = p.read_text(encoding='utf-8-sig')
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith('First Name'))
    return [(row.get('Company') or '').strip() for row in csv.DictReader(io.StringIO('\n'.join(lines[start:])))]


def assign_groups(companies):
    spell = {}
    for c in companies:
        if c:
            spell.setdefault(spell_key(c), Counter())[c] += 1
    best = {k: sorted(m.items(), key=lambda x: (-x[1], len(x[0])))[0][0] for k, m in spell.items()}

    def parent_of(k):
        w = k.split(' ')
        for n in range(len(w) - 1, 0, -1):
            p = re.sub(r'[\s\-–—:,(]+$', '', ' '.join(w[:n]))
            if len(p) < 4 or (n == 1 and p in PREFIX_STOP):
                continue
            if p in best and not group_of(best[p]):
                return best[p]
        return ''

    out = []
    for c in companies:
        if not c:
            out.append('')
            continue
        k = spell_key(c)
        out.append(group_of(c) or parent_of(k) or best.get(k) or c)
    return out


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    n_manq = int(args[args.index('--manquants') + 1]) if '--manquants' in args else 40
    groups = [g for g in assign_groups(read_companies(args[0])) if g and g not in NO_COMPANY_GROUPS]
    cnt = Counter(groups)
    logo = {g: bool(domain_of(g)) for g in cnt}
    tot = sum(cnt.values())
    big = {g: n for g, n in cnt.items() if n >= 2}
    tot_big = sum(big.values())
    pct = lambda a, b: f'{100 * a / b:.0f} %' if b else '–'
    print(f'Contacts avec une entreprise : {tot} ({len(cnt)} entreprises)')
    print(f'  avec logo : {pct(sum(n for g, n in cnt.items() if logo[g]), tot)}')
    print(f'Entreprises d’au moins 2 contacts : {tot_big} contacts ({len(big)} entreprises)')
    print(f'  avec logo : {pct(sum(n for g, n in big.items() if logo[g]), tot_big)} des contacts, '
          f'{sum(1 for g in big if logo[g])} entreprises sur {len(big)}')
    manq = [(g, n) for g, n in cnt.most_common() if not logo[g]][:n_manq]
    if manq:
        print(f'\nEntreprises sans logo les plus fréquentes :')
        for g, n in manq:
            print(f'  {n:4d}  {g}')


if __name__ == '__main__':
    main()
