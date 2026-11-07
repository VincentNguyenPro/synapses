# Vidéo de démo Synapses : script de la voix off

> Ancien film de démo (1 min 45), remplacé sur la landing le 7 novembre 2026 par le film de lancement (`script-yc.md`, `film-yc.html`) ; ses fichiers `assets/demo/synapses-demo*` ont été retirés du dépôt (historique git).

Durée totale : 1:48. Ton : posé, direct, tutoiement. Chaque phrase doit tenir dans sa fenêtre ; un léger silence en fin de fenêtre est normal.
Les trois premières secondes sont l’image de couverture (miniature dans les messageries) : la voix commence à 0:03.

| Début | Fin | À l’écran | Voix off |
|---|---|---|---|
| 0:00,0 | 0:03,0 | Couverture : Synapses et le graphe | *(silence)* |
| 0:03,0 | 0:06,2 | « Tu as 843 contacts LinkedIn. » | Tu as des centaines de contacts sur LinkedIn. |
| 0:06,2 | 0:10,8 | Liste de relations qui défile | Mais tu les vois un par un, dans une liste sans fin, triée par date. |
| 0:10,8 | 0:19,0 | Quatre questions | Qui tu connais chez Doctolib ? Qui peut t’ouvrir la porte d’un job ou d’un client ? Impossible de le savoir d’un coup d’œil. |
| 0:19,0 | 0:22,2 | Logo Synapses | Synapses transforme ta liste en carte de ton réseau. |
| 0:22,2 | 0:30,6 | Quatre cas d’usage | Pour décrocher une opportunité, développer ton business, préparer un rendez-vous, ou élargir ton réseau là où il te manque des contacts. |
| 0:30,6 | 0:37,6 | Récupérer l’export | D’abord, demande l’archive complète de tes données dans les préférences LinkedIn. Elle arrive par email. |
| 0:37,6 | 0:45,2 | 1. Dépose l’archive | Glisse l’archive telle quelle sur Synapses : elle est lue dans ton navigateur, et ton réseau apparaît. |
| 0:45,2 | 0:54,2 | 2. Regrouper par | Regroupe tes contacts comme tu veux : par secteur, entreprise, fonction, séniorité ou année de connexion. |
| 0:54,2 | 1:04,2 | 3. Secteur | Clique sur un secteur : tu vois qui tu y connais, à quel niveau, et les plus proches de toi en premier. |
| 1:04,2 | 1:15,2 | 4. Fiche contact | Choisis un contact : tu as toute sa fiche. Ton lien avec ce contact : vos messages, vos recommandations… et surtout ses collègues de la même entreprise. |
| 1:15,2 | 1:28,2 | 5. Porte d’entrée | Tu vises une entreprise ? Tape son nom : Synapses te montre qui peut t’ouvrir la porte, des plus seniors aux plus juniors. |
| 1:28,2 | 1:38,3 | 6. Par entreprise | Regroupe par entreprise, avec les logos en option : tu vois d’un coup d’œil où se concentrent tes contacts. |
| 1:38,3 | 1:42,7 | Cadenas | Et ton fichier ne quitte jamais ton navigateur. |
| 1:42,7 | 1:48,3 | Fin : URL | Synapses. Gratuit, sans inscription. Vois enfin ton réseau. |

## Miniature

- Messageries (WhatsApp, iMessage…) : elles prennent la première image, qui est la couverture.
- LinkedIn : au moment de publier la vidéo, téléverse `out/miniature-16x9.png` (ou `miniature-1x1.png`) comme miniature.
- Le MP4 embarque aussi la couverture comme pochette (Finder, VLC).
- Landing page : `assets/demo/synapses-demo.mp4` commence directement sur « Tu as … contacts » (l’affiche du lecteur montre déjà la couverture). Couper les 3 premières secondes et décaler les sous-titres d’autant :

```bash
ffmpeg -i video/out/synapses-16x9.mp4 -ss 3 -map 0:0 -map 0:1 -c:v libx264 -preset slow -crf 30 -tune stillimage -pix_fmt yuv420p -af "afade=t=in:d=0.12" -c:a aac -b:a 128k -movflags +faststart assets/demo/synapses-demo.mp4
```

## Fabriquer la bande-son et la vidéo

Une seule fois : `cd video && npm install` (il faut aussi ffmpeg, Python avec numpy et scipy, et Google Chrome).

1. La voix : ElevenLabs, voix « Charlie », modèle v3, phrase par phrase et calée sur ce tableau. La clé est lue dans `~/.config/synapses/elevenlabs.env`, jamais dans le dépôt.

```bash
node video/voix-ia.js Charlie
```

2. La musique, composée par code et calée sur les mêmes scènes, puis le mélange (la musique baisse quand la voix parle) :

```bash
python3 video/musique.py && sh video/mixer.sh
```

3. Le rendu des deux formats ; le script sert lui-même les fichiers en local :

```bash
node video/render.js 169 video/out/bande-son.m4a && node video/render.js 11 video/out/bande-son.m4a
```

Version anglaise : même minutage, script `script-voix-off-en.md`, `node video/voix-ia.js Charlie --en`, `sh video/mixer.sh en`, `node video/render.js 169 video/out/bande-son-en.m4a --en` (textes du film en anglais par `?lang=en`). Sur le site : `assets/demo/synapses-demo-en.mp4`, coupé et réencodé comme la version française ci-dessous, avec `synapses-demo-en.vtt` et l’affiche `synapses-demo-affiche-en.webp`.

Pour enregistrer ta propre voix à la place : lis le tableau sur la vidéo muette (`node video/render.js 169` la produit), exporte `voix-ia.m4a` dans `video/out/`, puis reprends à l’étape 2.

## Refilmer les plans de l’app

Après un changement de l’app, `node video/record.js` refilme les plans dans `clips/`. Il lui faut un serveur local à la racine du dépôt :

```bash
python3 -m http.server 8765
```
