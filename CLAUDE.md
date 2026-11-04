# Synapses — consignes pour Claude Code

## Le produit
Synapses visualise un réseau LinkedIn en graphe neuronal à partir de l’export LinkedIn de l’utilisateur (archive .zip ou Connections.csv).
Site public gratuit (GitHub Pages, branche `main`, dossier racine) :
  - https://vincentnguyenpro.github.io/synapses/ : landing page de présentation (`index.html`), le lien à partager, notamment aux recruteurs ;
  - https://vincentnguyenpro.github.io/synapses/app/ : l’outil (`app/index.html`).
Propriétaire : Vincent Nguyen, Product Manager. Langue de l’interface et des échanges : français.

## Principes non négociables
- **Le fichier importé et les données de contact ne quittent pas le navigateur.** Jamais de nom, d’URL de profil ni d’email d’un contact envoyé où que ce soit. Pas d’analytics.
- **Réseau gardé sur l’appareil** (choix de Vincent du 4 novembre 2026) : case « Garder mon réseau sur cet appareil », **décochée par défaut**, proposée par un bandeau après l’import.
  Cochée, les champs bruts de Connections.csv **sans les emails** sont enregistrés dans IndexedDB (`synapses-reseau`) et le réseau est rouvert au chargement ; décochée ou « Effacer mes données », la base est supprimée. Rien n’est envoyé.
- **Seule exception, le dictionnaire partagé (Supabase, projet `afvmshbacxaznhmlgkzc`, région UE)** — choix de Vincent du 2 novembre 2026 :
  - lecture : la page télécharge les ajouts validés (`dict_entreprises`, `dict_postes`) sans rien envoyer de l’utilisateur ;
  - écriture : uniquement si l’utilisateur coche « Partager mes corrections » (désactivé par défaut) ; seuls partent un nom d’entreprise ou un intitulé de poste et la catégorie choisie, dans `contributions` ;
  - une contribution n’entre dans le dictionnaire qu’après validation par Vincent (`statut = 'validee'`). Schéma et droits : `supabase/schema.sql`.
- **Classement par IA (« Choisir une IA »)**, à l’initiative de l’utilisateur et avec **sa propre clé API** (Anthropic, OpenAI ou Google) :
  la page appelle directement le fournisseur choisi depuis le navigateur ; seuls partent les noms d’entreprises et intitulés de poste non reconnus.
  La clé n’est envoyée qu’à ce fournisseur et n’est gardée (localStorage) que si l’utilisateur coche « Se souvenir de ma clé ». Un vrai « connecter mon compte » n’existe pas chez ces fournisseurs.
  Modèles proposés (`PROVIDERS` dans `app/index.html`) : à revoir quand les fournisseurs en retirent.
  Erreurs (`callLLM`) : clé refusée, crédit épuisé (`insufficient_quota`, « credit balance ») et limite de débit sont distingués ; une limite de débit (429, 5xx) est retentée jusqu’à 5 fois (`callLLMRetry`, délai annoncé par le fournisseur) avant d’afficher l’explication. Le 429 de Gemini parle de « billing » sans être un manque de crédit.
- **Logos des entreprises (Brandfetch Logo API)** : option « Logos des entreprises » du panneau Affichage, **cochée par défaut** (choix de Vincent du 3 novembre 2026), décochable ; l’utilisateur est informé à côté de la case et dans « Tes données ».
  Cochée, chaque logo affiché envoie à `cdn.brandfetch.io` le domaine de l’entreprise (et l’IP du visiteur), jamais le nom d’un contact.
  Client ID public dans `LOGO_CONFIG` ; `fallback/404` pour qu’une marque inconnue garde son monogramme.
  Domaines dans `data/domaines.json` (vérifiés à la main) : **aucun domaine n’est deviné** (« laposte.com » affichait le logo d’une autre marque) ; une entreprise absente garde son monogramme. Pour ajouter un logo, ajouter son domaine officiel dans ce fichier.
- **Compteur anonyme des réseaux visualisés** (choix de Vincent du 3 novembre 2026) : après un import réussi, l’outil appelle `compter_soumission()` (au plus une fois par jour et par navigateur) ; rien d’autre n’est envoyé. La landing page lit le total et l’affiche en grand sous la vidéo du héros, quel qu’il soit (choix de Vincent du 4 novembre 2026, le seuil de 50 est abandonné) ; si la base ne répond pas, rien n’est affiché. Mentionné dans « Tes données ». Schéma : `supabase/compteur.sql`. Ne jamais afficher un chiffre gonflé.
- **Pas de Google Fonts ni de ressource tierce traçante** (RGPD). Seules exceptions : D3, PapaParse et JSZip depuis cdnjs (versions figées, empreintes SRI), l’API Supabase ci-dessus, l’API du fournisseur d’IA choisi par l’utilisateur et Brandfetch (option logos, cochée par défaut).
- **Outil indépendant, non affilié à LinkedIn** : pas de logo LinkedIn, pas de formulation laissant croire à un partenariat.
- Tout le code est public : ne jamais y mettre de clé d’API, de jeton ou de donnée personnelle. Seule exception : la clé **publishable** Supabase (`sb_publishable_…`), publique par conception. Jamais la clé secrète (`sb_secret_…`).

## Architecture
- Outil : un seul fichier `app/index.html` (HTML, CSS et JS inline), sans étape de compilation. Il charge `../data/*.json` et les icônes de la racine.
- Landing page : `index.html` à la racine, page statique avec les captures de démonstration de `assets/demo/` (réseau fictif uniquement, jamais de vraies données) ; bouton « Essayer la démo » → `app/` ; le lien « ton export » de la fin de page mène à `app/#importer`.
  Pour refaire les captures : démo, 1600 × 1000, navigateur visible (Brandfetch bloque les navigateurs headless), WebP en 1600 et 900 px.
  Vidéo, dans le héros à côté du titre (codes YC ; le graphe interactif de démo est dans la section sombre en dessous) : le film (`assets/demo/synapses-demo.mp4`, voix off, sous-titres) ne se lance qu’au clic ; un aperçu muet de 8 s en boucle (`synapses-apercu.mp4`, extrait 1:03–1:11 recadré au bord de la fenêtre de l’outil, `crop=1156:650:701:212`) tourne quand le lecteur est visible, jamais avec « moins d’animations » ou l’économie de données.
- Import : `handleFiles` lit le .zip (JSZip) et y cherche `Connections.csv`, `Profile.csv`, `Positions.csv`.
  Format réel de Connections.csv : 3 lignes de notes, puis `First Name,Last Name,URL,Email Address,Company,Position,Connected On`, dates du type `17 Jan 2026`.
  `Email Address` n’est rempli que pour les contacts qui ont autorisé son partage : l’email s’affiche alors dans la fiche (lien `mailto:`), sans jamais être enregistré ni envoyé.
- Dictionnaires de classification dans `data/` (fichiers statiques chargés au démarrage par `loadDictionary`) :
  `data/entreprises.json` (entreprise → secteur, mots-clés de secteur) et `data/postes.json` (mots-clés de fonction, règles de séniorité).
  Pour enrichir la classification, modifier ces fichiers, pas `app/index.html`. Ne jamais y ajouter un nom de personne.
- Classification, par ordre de priorité : correction de l’utilisateur (localStorage) > ajout validé du dictionnaire partagé (Supabase) > dictionnaire `data/entreprises.json` (variantes « Groupe X », « x.fr », « A - B » comprises) > mots-clés.
- Vues (section « Vues » du panneau) : une vue = regroupement, couleurs, branches, mode, filtres, années, recherche ; jamais de contact ni de sélection.
  Vues prêtes à l’emploi (`presets`), « Mes vues » (localStorage `synapses-views-v1`), dernière vue (`synapses-lastview-v1`, restaurée par `load` au démarrage et après un import) et lien `#vue=…` (JSON en base64url, **sans la recherche**, qui peut contenir un nom de contact).
  `setView` ignore les valeurs absentes du réseau chargé et ramène les années à celles disponibles.
- Classement par IA : bandeau refermable après import, et entrée permanente « Classification par IA » dans le panneau Affichage (`syncAIField`).
- Graphe (D3) : « Moi » au centre, groupes sur un cercle à angles égaux (ordre croissant depuis midi, sens horaire), contacts en grappes homogènes par valeur de « Colorer par ».
- Performance (mesurée jusqu’à 5 000 contacts, ~10 000 éléments SVG) : ne jamais mettre `opacity` sur les éléments du graphe
  (chaque élément est alors dessiné à part) — estomper avec `fill-opacity` / `stroke-opacity` ; pas de fondu au-delà de 2 500 contacts
  (classe `heavy`) ; `ticked` ne réécrit que les points qui ont bougé ; la largeur des noms de groupes est mise en cache (`__w13`).
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
