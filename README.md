# Synapses

Visualise ton réseau LinkedIn sous forme de graphe neuronal, à partir de ton export LinkedIn.

- Gratuit, sans inscription.
- Ton fichier est lu dans ton navigateur : il n’est envoyé nulle part, et les noms de tes contacts ne quittent jamais ton appareil.
- Option « Choisir une IA » : avec ta propre clé API Claude (Anthropic), ChatGPT (OpenAI) ou Gemini (Google), une IA classe les entreprises et intitulés de poste que le dictionnaire ne reconnaît pas. Seuls ces noms et intitulés sont envoyés au fournisseur choisi ; ta clé n’est envoyée qu’à lui et n’est gardée sur ton appareil que si tu le demandes.
- Option « Garder mon réseau sur cet appareil » (désactivée par défaut) : ton réseau est rouvert après un rafraîchissement sans réimporter ton fichier. Il reste dans ton navigateur, sans les emails, et n’est envoyé nulle part.
- Proximité : dans les fiches, tes contacts sont classés du plus proche au moins proche (messages échangés, recommandations, compétences recommandées, entreprises et écoles en commun). Le texte de tes messages n’est jamais lu ; rien n’est envoyé.
- Vues : des vues prêtes à l’emploi (Décideurs, Juniors à recommander, Contacts récents, Par entreprise), tes propres vues enregistrées dans ton navigateur, la dernière vue retrouvée à ta prochaine visite, et un lien pour partager une vue. Ce lien ne contient que les réglages (regroupement, couleurs, filtres), jamais tes contacts ni ta recherche.
- Logos des entreprises (activés par défaut, désactivables dans Affichage) : les logos viennent de [Brandfetch](https://brandfetch.com), qui reçoit le site web des entreprises affichées, jamais le nom de tes contacts.
- Option « Partager mes corrections » (désactivée par défaut) : quand tu corriges un secteur, une fonction ou une séniorité, seuls le nom de l’entreprise ou l’intitulé du poste et la catégorie choisie sont proposés au dictionnaire partagé.
- Compteur anonyme : chaque import ajoute 1 au nombre de réseaux visualisés affiché sur la page d’accueil (au plus une fois par jour et par navigateur), sans rien envoyer d’autre.
- Outil indépendant, non affilié à LinkedIn.

Page de présentation : https://vincentnguyenpro.github.io/synapses/ · Outil : https://vincentnguyenpro.github.io/synapses/app/

## Utilisation

1. Sur LinkedIn : Préférences › Confidentialité des données › Obtenir une copie de vos données, puis demande l’archive.
2. Ouvre Synapses et importe l’archive `.zip` reçue par email (ou seulement `Connections.csv`).

## Mise en ligne avec GitHub Pages

1. Crée un dépôt public, par exemple `synapses`.
2. Dépose les fichiers du dépôt tels quels : `index.html` (page de présentation) à la racine, l’outil dans `app/`, les dictionnaires dans `data/`, les captures dans `assets/demo/`.
3. Dans le dépôt : Settings › Pages › Build and deployment › Source : « Deploy from a branch », branche `main`, dossier `/ (root)`, puis Save.
4. Après une à deux minutes, le site est en ligne à l’adresse `https://<ton-identifiant>.github.io/synapses/`.

Pour mettre à jour le site, pousse les fichiers modifiés sur `main` : GitHub Pages republie automatiquement.

## Fonctionnement technique

- L’outil tient dans un seul fichier HTML (`app/index.html`), sans étape de compilation ; la page de présentation (`index.html`) est statique.
- Bibliothèques chargées depuis cdnjs : D3 (graphe), PapaParse (CSV), JSZip (archive).
- Secteur, fonction et séniorité sont estimés dans le navigateur à partir des dictionnaires du dossier `data/` : `entreprises.json` (entreprises et mots-clés par secteur) et `postes.json` (mots-clés de fonction et règles de séniorité). Chaque estimation peut être corrigée depuis la fiche d’un contact.
- Les tags, vues et corrections sont enregistrés dans le stockage local du navigateur ; le réseau, si l’utilisateur le demande, dans IndexedDB (sans les emails).
- Dictionnaire partagé : base Supabase hébergée dans l’Union européenne (schéma et droits d’accès dans `supabase/schema.sql`). Le public peut lire les ajouts validés et proposer des corrections ; une proposition n’entre dans le dictionnaire qu’après validation.
- Compteur : `supabase/compteur.sql` (une ligne, un total ; le public peut seulement le lire et l’augmenter de 1).

## Modérer les propositions

Dans Supabase › Table Editor › `contributions`, passe le statut d’une ligne à `validee` (ou `refusee`) : une ligne validée entre aussitôt dans le dictionnaire partagé. Dans SQL Editor, `select * from a_valider;` regroupe les propositions identiques, et `select valider_consensus(3);` valide d’un coup celles proposées au moins 3 fois.

## Droits

© 2026 Vincent Nguyen. Tous droits réservés.
Le code est visible pour la transparence, mais sa réutilisation, sa modification ou sa redistribution nécessitent une autorisation écrite.
