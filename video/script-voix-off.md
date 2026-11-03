# Vidéo de démo Synapses : script de la voix off

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
| 0:30,6 | 0:37,6 | Récupérer l’export | D’abord, demande ton export dans les préférences LinkedIn, en cochant « Relations ». L’archive arrive par email. |
| 0:37,6 | 0:45,2 | 1. Dépose l’archive | Glisse l’archive telle quelle sur Synapses : elle est lue dans ton navigateur, et ton réseau apparaît. |
| 0:45,2 | 0:54,2 | 2. Regrouper par | Regroupe tes contacts comme tu veux : par secteur, entreprise, fonction, séniorité, formation ou ville. |
| 0:54,2 | 1:02,2 | 3. Colorer par | Et colore-les selon ce qui compte pour toi : la séniorité, la fonction, l’année de connexion. |
| 1:02,2 | 1:07,7 | 4. Secteur | Clique sur un secteur pour voir qui tu y connais, et à quel niveau. |
| 1:07,7 | 1:18,7 | 5. Fiche contact | Choisis un contact : tu as toute sa fiche. Secteur, fonction, formation, ville, date de connexion… et surtout ses collègues de la même entreprise et les anciens de son école. |
| 1:18,7 | 1:23,7 | 6. Filtres | Filtre en un clic : juniors, seniors, secteurs, fonctions. |
| 1:23,7 | 1:28,3 | 7. Par entreprise | Regroupe par entreprise pour voir où se concentrent tes contacts. |
| 1:28,3 | 1:38,3 | 8. Branches | Le curseur « Branches affichées » montre les plus gros groupes… ou ton réseau en entier, toutes les entreprises d’un coup. |
| 1:38,3 | 1:42,7 | Cadenas | Et ton fichier ne quitte jamais ton navigateur. |
| 1:42,7 | 1:48,3 | Fin : URL | Synapses. Gratuit, sans inscription. Vois enfin ton réseau. |

## Miniature

- Messageries (WhatsApp, iMessage…) : elles prennent la première image, qui est la couverture.
- LinkedIn : au moment de publier la vidéo, téléverse `out/miniature-16x9.png` (ou `miniature-1x1.png`) comme miniature.
- Le MP4 embarque aussi la couverture comme pochette (Finder, VLC).

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

Pour enregistrer ta propre voix à la place : lis le tableau sur la vidéo muette (`node video/render.js 169` la produit), exporte `voix-ia.m4a` dans `video/out/`, puis reprends à l’étape 2.

## Refilmer les plans de l’app

Après un changement de l’app, `node video/record.js` refilme les plans dans `clips/`. Il lui faut un serveur local à la racine du dépôt :

```bash
python3 -m http.server 8765
```
