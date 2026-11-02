# Synapses

Visualise ton réseau LinkedIn sous forme de graphe neuronal, à partir de ton export LinkedIn.

- Gratuit, sans inscription.
- Ton fichier est lu dans ton navigateur : il n’est envoyé nulle part, et les noms de tes contacts ne quittent jamais ton appareil.
- Option « Choisir une IA » : avec ta propre clé API Claude (Anthropic), ChatGPT (OpenAI) ou Gemini (Google), une IA classe les entreprises et intitulés de poste que le dictionnaire ne reconnaît pas. Seuls ces noms et intitulés sont envoyés au fournisseur choisi ; ta clé n’est envoyée qu’à lui et n’est gardée sur ton appareil que si tu le demandes.
- Logos des entreprises (activés par défaut, désactivables dans Affichage) : les logos viennent de [Brandfetch](https://brandfetch.com), qui reçoit le site web des entreprises affichées, jamais le nom de tes contacts.
- Option « Partager mes corrections » (désactivée par défaut) : quand tu corriges un secteur, une fonction ou une séniorité, seuls le nom de l’entreprise ou l’intitulé du poste et la catégorie choisie sont proposés au dictionnaire partagé.
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
- Dictionnaire partagé : base Supabase hébergée dans l’Union européenne (schéma et droits d’accès dans `supabase/schema.sql`). Le public peut lire les ajouts validés et proposer des corrections ; une proposition n’entre dans le dictionnaire qu’après validation.

## Modérer les propositions

Dans Supabase › Table Editor › `contributions`, passe le statut d’une ligne à `validee` (ou `refusee`) : une ligne validée entre aussitôt dans le dictionnaire partagé. Dans SQL Editor, `select * from a_valider;` regroupe les propositions identiques, et `select valider_consensus(3);` valide d’un coup celles proposées au moins 3 fois.

## Droits

© 2026 Vincent Nguyen. Tous droits réservés.
Le code est visible pour la transparence, mais sa réutilisation, sa modification ou sa redistribution nécessitent une autorisation écrite.
