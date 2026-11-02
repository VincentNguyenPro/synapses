# Synapses

Visualise ton réseau LinkedIn sous forme de graphe neuronal, à partir de ton export LinkedIn.

- Gratuit, sans inscription.
- Ton fichier est lu dans ton navigateur : aucun serveur, aucune donnée stockée en ligne.
- Outil indépendant, non affilié à LinkedIn.

## Utilisation

1. Sur LinkedIn : Préférences › Confidentialité des données › Obtenir une copie de vos données, puis demande l’archive.
2. Ouvre Synapses et importe l’archive `.zip` reçue par email (ou seulement `Connections.csv`).

## Mise en ligne avec GitHub Pages

1. Crée un dépôt public, par exemple `synapses`.
2. Dépose `index.html` (et ce `README.md`) à la racine du dépôt.
3. Dans le dépôt : Settings › Pages › Build and deployment › Source : « Deploy from a branch », branche `main`, dossier `/ (root)`, puis Save.
4. Après une à deux minutes, le site est en ligne à l’adresse `https://<ton-identifiant>.github.io/synapses/`.

Pour mettre à jour le site, remplace `index.html` dans le dépôt : GitHub Pages republie automatiquement.

## Fonctionnement technique

- Un seul fichier HTML, sans étape de compilation.
- Bibliothèques chargées depuis cdnjs : D3 (graphe), PapaParse (CSV), JSZip (archive).
- Secteur, fonction et séniorité sont estimés dans le navigateur à partir des dictionnaires du dossier `data/` : `entreprises.json` (entreprises et mots-clés par secteur) et `postes.json` (mots-clés de fonction et règles de séniorité). Chaque estimation peut être corrigée depuis la fiche d’un contact.
- Les tags et corrections sont enregistrés dans le stockage local du navigateur.

## Droits

© 2026 Vincent Nguyen. Tous droits réservés.
Le code est visible pour la transparence, mais sa réutilisation, sa modification ou sa redistribution nécessitent une autorisation écrite.
