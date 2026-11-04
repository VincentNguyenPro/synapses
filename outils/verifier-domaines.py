#!/usr/bin/env python3
"""Vérifie des domaines candidats avant de les ajouter à data/domaines.json (logos Brandfetch).

Usage : python3 -I outils/verifier-domaines.py candidats.tsv [--ajouter]

candidats.tsv : une ligne par entreprise, « clé<TAB>domaine », la clé écrite comme dans data/domaines.json
(nom en minuscules, sans accents, apostrophes remplacées par une espace). Les lignes vides ou commençant par # sont ignorées.

Pour chaque domaine, le script :
  1. ouvre le site et relève l’adresse finale (redirections) et le titre de la page ;
  2. regarde si le nom de l’entreprise apparaît dans ce titre ou dans l’adresse finale ;
  3. demande à Brandfetch si un logo existe (sinon l’app garderait l’initiale de toute façon).
Verdict : « ok » (nom retrouvé et logo présent), « sans logo », « à revoir » (nom non retrouvé, site muet ou bloqué,
redirection vers un autre nom). Seuls les « ok » sont ajoutés avec --ajouter ; les autres se vérifient à la main.
Aucun domaine n’est jamais deviné : le script ne fait que contrôler ceux qu’on lui donne.
"""
import json, re, sys, unicodedata, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

RACINE = Path(__file__).resolve().parent.parent
FICHIER = RACINE / 'data/domaines.json'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'
LOGO = 'https://cdn.brandfetch.io/domain/{d}/w/128/h/128/fallback/404/type/icon?c=1idZzRfYk3Zw3y_iDaq'
VIDES = {'groupe', 'group', 'france', 'the', 'les', 'des', 'and', 'cie', 'compagnie', 'societe', 'banque', 'conseil',
         'consulting', 'ministere', 'departement', 'ville', 'universite', 'ecole', 'institut', 'agence'}


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    return ''.join(c for c in s if not unicodedata.combining(c))


def get(url, limit=400_000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'fr,en;q=0.8'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.geturl(), r.read(limit).decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.geturl() if hasattr(e, 'geturl') else url, ''
    except Exception as e:
        return 0, url, ''


def base(host):
    parts = (host or '').lower().removeprefix('www.').split('.')
    return '.'.join(parts[-3:]) if len(parts) > 2 and parts[-2] in ('co', 'com', 'gouv') else '.'.join(parts[-2:])


def verifier(cle, dom):
    code, final, html = get('https://' + dom)
    if code == 0:
        code, final, html = get('https://www.' + dom)
    titre = ' '.join(unescape(m) for m in re.findall(r'<title[^>]*>([^<]*)', html, re.I)[:1]
                     + re.findall(r'og:site_name"\s+content="([^"]*)', html, re.I)[:1]).strip()
    titre = re.sub(r'\s+', ' ', titre)[:90]
    texte = norm(titre + ' ' + final).replace('-', ' ')
    mots = [w for w in re.split(r'[^a-z0-9]+', norm(cle)) if len(w) >= 3 and w not in VIDES] or [norm(cle)]
    nom_vu = any(w in texte or w in texte.replace(' ', '') for w in mots)
    lcode = get(LOGO.format(d=dom), 2000)[0]
    autre = base(urlparse(final).hostname) != base(dom)
    if code == 0:
        verdict = 'à revoir (site muet)'
    elif not nom_vu and code < 400:
        verdict = 'à revoir (nom absent)'
    elif autre and not nom_vu:
        verdict = 'à revoir (redirection)'
    elif lcode != 200:
        verdict = 'sans logo'
    elif code >= 400 and not nom_vu:
        verdict = 'à revoir (site bloqué)'
    else:
        verdict = 'ok'
    return cle, dom, verdict, code, final, titre


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    data = json.loads(FICHIER.read_text(encoding='utf-8'))
    doms = data['domaines']
    lignes = [l.rstrip('\n').split('\t') for l in Path(args[0]).read_text(encoding='utf-8').splitlines()
              if l.strip() and not l.startswith('#')]
    cands = [(c.strip(), d.strip().lower()) for c, d in lignes if c.strip() not in doms]
    deja = len(lignes) - len(cands)
    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(lambda x: verifier(*x), cands))
    for cle, dom, verdict, code, final, titre in sorted(res, key=lambda r: (r[2] != 'ok', r[2], r[0])):
        print(f'{verdict:24} {cle:38} {dom:28} {code} {final[:60]:60} {titre}')
    ok = [(c, d) for c, d, v, *_ in res if v == 'ok']
    print(f'\n{len(ok)} ok, {len(res) - len(ok)} à revoir ou sans logo, {deja} déjà présents')
    if '--ajouter' in args and ok:
        doms.update(ok)
        data['domaines'] = dict(sorted(doms.items()))
        FICHIER.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f'{len(ok)} domaines ajoutés à {FICHIER.relative_to(RACINE)} ({len(doms)} au total)')


if __name__ == '__main__':
    main()
