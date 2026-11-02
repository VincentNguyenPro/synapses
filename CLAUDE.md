# Synapses — consignes pour Claude Code

## Le produit
Synapses visualise un réseau LinkedIn en graphe neuronal à partir de l’export LinkedIn de l’utilisateur (archive .zip ou Connections.csv).
Site public gratuit : https://vincentnguyenpro.github.io/synapses/ (GitHub Pages, branche `main`, dossier racine).
Propriétaire : Vincent Nguyen, Product Manager. Langue de l’interface et des échanges : français.

## Principes non négociables
- **Le fichier importé et les données de contact ne quittent pas le navigateur.** Jamais de nom, d’URL de profil ni d’email d’un contact envoyé où que ce soit. Pas d’analytics.
- **Seule exception, le dictionnaire partagé (Supabase, projet `afvmshbacxaznhmlgkzc`, région UE)** — choix de Vincent du 2 novembre 2026 :
  - lecture : la page télécharge les ajouts validés (`dict_entreprises`, `dict_postes`) sans rien envoyer de l’utilisateur ;
  - écriture : uniquement si l’utilisateur coche « Partager mes corrections » (désactivé par défaut) ; seuls partent un nom d’entreprise ou un intitulé de poste et la catégorie choisie, dans `contributions` ;
  - une contribution n’entre dans le dictionnaire qu’après validation par Vincent (`statut = 'validee'`). Schéma et droits : `supabase/schema.sql`.
- **Classement par IA (« Choisir une IA »)**, à l’initiative de l’utilisateur et avec **sa propre clé API** (Anthropic, OpenAI ou Google) :
  la page appelle directement le fournisseur choisi depuis le navigateur ; seuls partent les noms d’entreprises et intitulés de poste non reconnus.
  La clé n’est envoyée qu’à ce fournisseur et n’est gardée (localStorage) que si l’utilisateur coche « Se souvenir de ma clé ». Un vrai « connecter mon compte » n’existe pas chez ces fournisseurs.
  Modèles proposés (`PROVIDERS` dans `index.html`) : à revoir quand les fournisseurs en retirent.
- **Logos des entreprises (Brandfetch Logo API)** : option « Logos des entreprises » du panneau Affichage, **décochée par défaut**.
  Cochée, chaque logo affiché envoie à `cdn.brandfetch.io` le domaine de l’entreprise (et l’IP du visiteur), jamais le nom d’un contact.
  Client ID public dans `LOGO_CONFIG` ; `fallback/404` pour qu’une marque inconnue garde son monogramme ; aucun domaine deviné pour « Freelance », « Confidentiel »… (`NOT_A_COMPANY`).
- **Pas de Google Fonts ni de ressource tierce traçante** (RGPD). Seules exceptions : D3, PapaParse et JSZip depuis cdnjs (versions figées, empreintes SRI), l’API Supabase ci-dessus, l’API du fournisseur d’IA choisi par l’utilisateur et Brandfetch si l’option logos est cochée.
- **Outil indépendant, non affilié à LinkedIn** : pas de logo LinkedIn, pas de formulation laissant croire à un partenariat.
- Tout le code est public : ne jamais y mettre de clé d’API, de jeton ou de donnée personnelle. Seule exception : la clé **publishable** Supabase (`sb_publishable_…`), publique par conception. Jamais la clé secrète (`sb_secret_…`).

## Architecture
- Un seul fichier `index.html` (HTML, CSS et JS inline), sans étape de compilation.
- Import : `handleFiles` lit le .zip (JSZip) et y cherche `Connections.csv`, `Profile.csv`, `Positions.csv`.
  Format réel de Connections.csv : 3 lignes de notes, puis `First Name,Last Name,URL,Email Address,Company,Position,Connected On`, dates du type `17 Jan 2026`.
- Dictionnaires de classification dans `data/` (fichiers statiques chargés au démarrage par `loadDictionary`) :
  `data/entreprises.json` (entreprise → secteur, mots-clés de secteur) et `data/postes.json` (mots-clés de fonction, règles de séniorité).
  Pour enrichir la classification, modifier ces fichiers, pas `index.html`. Ne jamais y ajouter un nom de personne.
- Classification, par ordre de priorité : correction de l’utilisateur (localStorage) > ajout validé du dictionnaire partagé (Supabase) > dictionnaire `data/entreprises.json` (variantes « Groupe X », « x.fr », « A - B » comprises) > mots-clés.
- Graphe (D3) : « Moi » au centre, groupes sur un cercle à angles égaux (ordre croissant depuis midi, sens horaire), contacts en grappes homogènes par valeur de « Colorer par ».
- Le code lié à claude.ai (`window.claude`, capacité `sample`) est inactif ici : sur le site public, le classement par IA passe par `callLLM` et la clé de l’utilisateur.

## Règles de design acquises (validées avec Vincent)
- Aucun chevauchement entre nœuds, grappes, jauges et noms de groupes (vérifier après chaque changement de disposition).
- Branches de même longueur autour de « Moi » ; le poids d’un groupe se lit par la teinte, la jauge, l’épaisseur de branche et le pourcentage.
- Sélection d’un contact : il va au centre de sa grappe, ses collègues de la même entreprise forment un cercle autour de lui, ordonnés par séniorité (Junior → Dirigeant) depuis midi.
- Filtres et légende en lignes avec un fin trait de poids ; sélection = case cochée + fond bleuté + bordure.
- Typographie française : apostrophe ’, guillemets « », espace insécable avant « : » et « % ».

## Méthode de travail
1. Expliquer en une phrase ce qui va changer avant de modifier.
2. Après modification, tester dans un navigateur (démo + import d’un export réel si disponible) et vérifier la console.
3. Montrer le résultat à Vincent, puis seulement après son accord : commit avec un message clair en français, puis push sur `main`.
4. Ne jamais pousser un fichier contenant une erreur de syntaxe JavaScript.
