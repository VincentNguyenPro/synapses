# Film de lancement Synapses, style YC : script de la voix off

Durée totale : 0:57. Inspiré des films de lancement YC (Voyager) : typographie géante, interface en gros plan, montage rapide, une preuve, une fin sur dégradé.
Ton : un fondateur qui présente son produit, à la première personne, tutoiement. Voix : celle de Vincent, clonée en local par Chatterbox (`voix-clone.py voix-vincent.m4a`, échantillon tiré des passages fluides de son enregistrement, jamais commité).
Images : `film-yc.html` (`node render.js 169 out/bande-son-yc.m4a --film yc`).

Musique : « Cinematic Space Journey – Interstellar Odyssey » de Lilliben, Pixabay
(https://pixabay.com/music/ambient-cinematic-space-journey-interstellar-odyssey-365175/), licence de contenu Pixabay :
gratuite, usage commercial permis, sans attribution ; le fichier seul ne doit pas être redistribué (`musique-pixabay*` hors de git).
Le morceau (1:19) part de 21,8 s : sa montée accompagne le problème, sa partie pleine le logo et les plans, sa fin celle du film.
  ffmpeg -ss 21.8 -i musique-pixabay.mp3 -t 57.4 -af "afade=t=in:d=0.8,aresample=48000" -ac 2 out/musique-pixabay-yc.wav
  MUSIQUE=musique-pixabay-yc.wav sh mixer.sh yc
Repli sans droits : `python3 musique-yc.py` (piano et cordes, synthétisés ici).

| Début | Fin | À l’écran | Voix off |
|---|---|---|---|
| 0:00,0 | 0:03,6 | Titre : SYNAPSES en géant sur le graphe | Je suis Vincent, et j’ai créé Synapses. |
| 0:03,6 | 0:08,4 | Mots géants : des centaines de contacts, aucune vue d’ensemble | Sur LinkedIn, tu as des centaines de contacts, et aucune vue d’ensemble. |
| 0:08,4 | 0:13,6 | Mur de contacts qui défile : « Une liste sans fin. » | Juste une liste sans fin. Qui tu connais, et où ? Impossible à dire. |
| 0:13,6 | 0:17,0 | Logo Synapses | Synapses en fait une carte. |
| 0:17,0 | 0:22,6 | 1. Dépose | Tu déposes ton export LinkedIn, et ton réseau apparaît. |
| 0:22,6 | 0:28,2 | 2. Regroupe | Tu le regroupes par secteur, entreprise, fonction ou séniorité. |
| 0:28,2 | 0:34,0 | 3. Plonge | Un clic sur un secteur : les plus proches de toi d’abord. |
| 0:34,0 | 0:41,0 | 4. Porte d’entrée | Une entreprise en tête ? Synapses te montre qui peut t’ouvrir la porte. |
| 0:41,0 | 0:46,4 | 5. Par entreprise | Et tu vois enfin où se concentre ton réseau. |
| 0:46,4 | 0:51,4 | Cadenas : 100 % dans ton navigateur | Tout se passe dans ton navigateur : ton fichier ne le quitte jamais. |
| 0:51,4 | 0:57,4 | Fin : URL | Synapses. Gratuit, sans inscription. Essaie-le sur ton propre réseau. |
