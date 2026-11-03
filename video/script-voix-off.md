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

## Enregistrer et assembler

1. Enregistre la voix d’une traite en lisant la vidéo muette (`out/synapses-16x9-sans-voix.mp4`) pour caler le rythme, par exemple avec Dictaphone ou QuickTime, et exporte `voix.m4a` dans ce dossier.
2. Une seule fois : `cd video && npm install` (il faut aussi ffmpeg et Google Chrome). Lance ensuite le serveur local à la racine du dépôt, puis le rendu avec la voix :

```bash
python3 -m http.server 8765
```

```bash
node video/render.js 169 video/voix.m4a && node video/render.js 11 video/voix.m4a
```

La même piste sert aux deux formats : le minutage est identique.

## Refilmer les plans de l’app

Après un changement de l’app, `node video/record.js` refilme les sept plans dans `clips/` (serveur local lancé).
