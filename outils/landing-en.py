#!/usr/bin/env python3
"""Génère la landing page anglaise (en/index.html) à partir de la française (index.html).

Usage : python3 outils/landing-en.py

Chaque phrase française est remplacée par sa traduction ; si une phrase a changé dans index.html,
le script s’arrête et la nomme : il suffit alors de mettre à jour la paire correspondante ici.
Les chemins (assets/, app/, icônes) sont réécrits pour la page servie depuis en/.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
s = (ROOT / 'index.html').read_text(encoding='utf-8')
missing = []


def rep(a, b, n=1):
    """Remplace a par b ; a doit apparaître exactement n fois."""
    global s
    if s.count(a) != n:
        missing.append(f'{s.count(a)}× au lieu de {n}× : {a[:110]}')
        return
    s = s.replace(a, b)


SITE = 'https://vincentnguyenpro.github.io/synapses/'

# ---------- En-tête ----------
rep('<html lang="fr">', '<html lang="en">')
rep('<title>Synapses, ton réseau LinkedIn en carte</title>', '<title>Synapses, your LinkedIn network as a map</title>')
rep('content="Synapses range tes contacts LinkedIn par secteur, entreprise et séniorité pour te montrer qui peut t’ouvrir une porte : un job, un client, un rendez-vous. Gratuit, sans inscription, ton fichier reste dans ton navigateur."',
    'content="Synapses sorts your LinkedIn contacts by industry, company and seniority to show you who can open a door: a job, a client, a meeting. Free, no sign-up, your file stays in your browser."')
rep(f'<link rel="canonical" href="{SITE}">', f'<link rel="canonical" href="{SITE}en/">')
rep('<meta property="og:locale" content="fr_FR">\n<meta property="og:locale:alternate" content="en_US">',
    '<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="fr_FR">')
rep(f'<meta property="og:url" content="{SITE}">', f'<meta property="og:url" content="{SITE}en/">')
rep('<meta property="og:title" content="Synapses, ton réseau LinkedIn en carte">', '<meta property="og:title" content="Synapses, your LinkedIn network as a map">')
rep('<meta property="og:description" content="Tes contacts LinkedIn rangés par secteur, entreprise et séniorité. Gratuit, sans inscription, ton fichier reste dans ton navigateur.">',
    '<meta property="og:description" content="Your LinkedIn contacts sorted by industry, company and seniority. Free, no sign-up, your file stays in your browser.">')
rep(f'<meta property="og:image" content="{SITE}og-image-2.png">', f'<meta property="og:image" content="{SITE}og-image-en.png">')
rep('<meta property="og:image:alt" content="Synapses : « Ton réseau LinkedIn, en carte. », le bouton Essayer la démo et l’outil qui regroupe des contacts par secteur">',
    '<meta property="og:image:alt" content="Synapses: “Your LinkedIn network, as a map.”, the Try the demo button and the tool grouping contacts by industry">')

# ---------- Barre ----------
rep('aria-label="Synapses, accueil"', 'aria-label="Synapses, home"')
rep('<a href="#situations">Situations</a>', '<a href="#situations">Use cases</a>', 2)
rep('<a href="#demarrer">Démarrer</a>', '<a href="#demarrer">Get started</a>', 2)
rep('<a href="#confidentialite">Confidentialité</a>', '<a href="#confidentialite">Privacy</a>', 2)
rep('<a href="#questions">Questions</a>', '<a href="#questions">FAQ</a>', 2)
rep('<a class="lang" href="en/" hreflang="en" lang="en" aria-label="English version">EN</a>',
    '<a class="lang" href="../" hreflang="fr" lang="fr" aria-label="Version française">FR</a>')
rep('Essayer la démo</a>', 'Try the demo</a>', 2)

# ---------- Héros ----------
rep('<h1 id="titre" class="rise">Ton réseau LinkedIn, en&nbsp;carte.</h1>', '<h1 id="titre" class="rise">Your LinkedIn network, as&nbsp;a&nbsp;map.</h1>')
rep('Synapses range tes contacts par secteur, entreprise et séniorité pour te montrer qui peut t’ouvrir une porte&nbsp;: un job, un client, un rendez-vous.',
    'Synapses sorts your contacts by industry, company and seniority to show you who can open a door: a job, a client, a meeting.')
rep('Gratuit, sans compte. Ton fichier est lu dans ton navigateur et n’est envoyé nulle part.',
    'Free, no account. Your file is read in your browser and never sent anywhere. The tool itself is in French for now.')
rep('aria-label="Vidéo de démonstration de Synapses sur un réseau fictif, 1 min 48"', 'aria-label="Synapses demo video on a fictional network, 1 min 48, in French"')
rep('Télécharger la vidéo de démonstration', 'Download the demo video')
rep('aria-label="Lire la vidéo de démonstration, 1 min 48"', 'aria-label="Play the demo video, in French, 1 min 48"')
rep('<span>Voir la vidéo · 1:48</span>', '<span>Watch the video (French) · 1:48</span>')
rep('aria-label="0 réseaux"', 'aria-label="0 networks"')
rep('<span>réseaux LinkedIn déjà visualisés avec Synapses</span><small>Compteur anonyme&nbsp;: +1 à chaque import réussi, au plus une fois par jour et par navigateur.</small>',
    '<span>LinkedIn networks already mapped with Synapses</span><small>Anonymous counter: +1 for each successful import, at most once a day per browser.</small>')

# ---------- Graphe de démo ----------
rep('Essaie ici, sur un réseau fictif</h2>', 'Try it here, on a fictional network</h2>')
rep('150 contacts inventés. Clique sur un secteur pour voir qui tu y connais, change la couleur des points.',
    '150 made-up contacts. Click an industry to see who you know there, change the color of the dots.')
rep('aria-label="Aperçu interactif du réseau de démonstration : 150 contacts fictifs"', 'aria-label="Interactive preview of the demo network: 150 fictional contacts"')
rep('aria-label="Graphe : Moi au centre, dix secteurs autour, chaque contact en point"', 'aria-label="Graph: Me at the center, ten industries around, each contact as a dot"')
rep('aria-label="Colorer les contacts par"', 'aria-label="Color contacts by"')
rep('<span>Colorer par</span>', '<span>Color by</span>')
rep('aria-pressed="true">Séniorité</button>', 'aria-pressed="true">Seniority</button>')
rep('aria-pressed="false">Fonction</button>', 'aria-pressed="false">Function</button>')
rep('aria-label="Légende des couleurs"', 'aria-label="Color legend"')

# ---------- Carrousel ----------
rep('L’outil, écran par écran</h3>', 'The tool, screen by screen</h3>')
rep('aria-label="Écrans de Synapses, défilement horizontal"', 'aria-label="Synapses screens, horizontal scroll"')
rep('data-t="Un secteur en gros plan" data-d="Un clic sur un groupe zoome dessus&nbsp;: ses contacts se rangent par séniorité, la fiche liste les personnes."',
    'data-t="An industry up close" data-d="Click a group to zoom in: its contacts line up by seniority, the side panel lists the people."')
rep('alt="Le secteur Tech et logiciel sélectionné, avec sa fiche et ses grappes par séniorité"', 'alt="The Tech and software industry selected, with its panel and its seniority clusters"')
rep('data-t="Les collègues d’un contact" data-d="Choisis quelqu’un&nbsp;: ses collègues de la même entreprise forment un cercle autour de lui, du junior au dirigeant."',
    'data-t="A contact’s colleagues" data-d="Pick someone: their colleagues at the same company form a circle around them, from junior to executive."')
rep('alt="Un contact sélectionné, entouré de ses collègues de la même entreprise"', 'alt="A selected contact, surrounded by colleagues from the same company"')
rep('data-t="Des filtres qui se combinent" data-d="Juniors et seniors seulement&nbsp;: le graphe se recompose et se recentre aussitôt."',
    'data-t="Filters that combine" data-d="Juniors and seniors only: the graph rearranges and recenters at once."')
rep('alt="Le réseau filtré sur les juniors et les seniors"', 'alt="The network filtered on juniors and seniors"')
rep('data-t="Par entreprise, logos compris" data-d="Chaque entreprise devient un nœud avec son logo. Tu vois où se concentrent tes contacts."',
    'data-t="By company, logos included" data-d="Each company becomes a node with its logo. You see where your contacts cluster."')
rep('alt="Le réseau regroupé par entreprise, chaque nœud portant le logo de l’entreprise"', 'alt="The network grouped by company, each node showing the company’s logo"')
rep('data-t="L’aide pour récupérer ton export" data-d="Le panneau d’aide explique où demander l’archive à LinkedIn, et quoi en faire."',
    'data-t="Help to get your export" data-d="The help panel explains where to request the archive from LinkedIn, and what to do with it."')
rep('alt="Le panneau « Récupérer tes contacts LinkedIn » qui explique comment obtenir son export"', 'alt="The help panel explaining how to get your LinkedIn export"')
rep('aria-label="Écran précédent"', 'aria-label="Previous screen"')
rep('aria-label="Écran suivant"', 'aria-label="Next screen"')

# ---------- Situations ----------
rep('<span class="soft">Quatre situations.</span> Ce que tu y vois.', '<span class="soft">Four situations.</span> What you see.')
rep('aria-label="Situations"', 'aria-label="Use cases"')
rep('<b>Postuler</b><span>chez BlaBlaCar</span>', '<b>Apply</b><span>at BlaBlaCar</span>')
rep('<b>Prospecter</b><span>dans la banque</span>', '<b>Prospect</b><span>in banking</span>')
rep('<b>Rendez-vous</b><span>chez BNP Paribas</span>', '<b>Meeting</b><span>at BNP Paribas</span>')
rep('<b>Élargir</b><span>ton réseau</span>', '<b>Grow</b><span>your network</span>')
rep('Tu cliques sur un contact de BlaBlaCar&nbsp;: ses collègues apparaissent, rangés par séniorité. Tu sais à qui demander une recommandation.',
    'You click a BlaBlaCar contact: their colleagues appear, sorted by seniority. You know who to ask for a referral.')
rep('Tu gardes le secteur Banque et assurance et les niveaux Senior à Dirigeant&nbsp;: voilà les décideurs à appeler.',
    'You keep the Banking and insurance industry and the Senior to Executive levels: these are the decision-makers to call.')
rep('Tu regroupes par entreprise et tu ouvres BNP Paribas&nbsp;: tous tes contacts sur place, avec leur poste, avant d’entrer en réunion.',
    'You group by company and open BNP Paribas: all your contacts there, with their roles, before you walk into the meeting.')
rep('Les branches les plus fines montrent où il te manque du monde. Ici, la santé et le secteur public.',
    'The thinnest branches show where you’re missing people. Here, healthcare and the public sector.')
rep('Exemples tirés du réseau de démonstration, 150 contacts fictifs.', 'Examples from the demo network, 150 fictional contacts.')

# ---------- Démarrer ----------
rep('Trois gestes, sans compte</h2>', 'Three steps, no account</h2>')
rep('<strong>D’abord, demande ton export.</strong><p>Sur LinkedIn&nbsp;: Préférences, Confidentialité des données, «&nbsp;Obtenir une copie de vos données&nbsp;». Coche «&nbsp;Relations&nbsp;». <a href="https://www.linkedin.com/mypreferences/d/download-my-data" target="_blank" rel="noopener">Ouvrir la page de LinkedIn&nbsp;↗</a></p>',
    '<strong>First, request your export.</strong><p>On LinkedIn: Settings, Data privacy, “Get a copy of your data”. Tick “Connections”. <a href="https://www.linkedin.com/mypreferences/d/download-my-data" target="_blank" rel="noopener">Open the LinkedIn page&nbsp;↗</a></p>')
rep('<strong>Puis dépose l’archive.</strong><p>Le .zip tel quel, quand l’email de LinkedIn arrive, en général une dizaine de minutes plus tard. Il est lu sur ton appareil.</p>',
    '<strong>Then drop the archive.</strong><p>The .zip as is, once LinkedIn’s email arrives, usually about ten minutes later. It’s read on your device.</p>')
rep('<strong>Enfin, explore ta carte.</strong><p>Regroupe, colore, filtre, ouvre la fiche d’un contact. En attendant l’email, la démo marche déjà.</p>',
    '<strong>Finally, explore your map.</strong><p>Group, color, filter, open a contact’s profile. While you wait for the email, the demo already works.</p>')
rep('alt="Page « Télécharger mes données » de LinkedIn, dans Préférences, Confidentialité des données"', 'alt="LinkedIn’s “Download your data” page, in Settings, Data privacy (French interface)"')
rep('<figcaption>Sur LinkedIn&nbsp;: Préférences, Confidentialité des données. Quand l’archive est prête, «&nbsp;Télécharger les archives&nbsp;».</figcaption>',
    '<figcaption>On LinkedIn: Settings, Data privacy. When the archive is ready, “Download archive”.</figcaption>')
rep('<div class="drop">Dépose ton fichier Connections.csv</div>', '<div class="drop">Drop your Connections.csv file</div>')
rep('<p class="ok">150 contacts importés</p>', '<p class="ok">150 contacts imported</p>')
rep('<h4>Mon réseau</h4>', '<h4>My network</h4>')
rep('<span>secteurs</span>', '<span>industries</span>')
rep('<span>entreprises</span>', '<span>companies</span>')
rep('<span>à un poste de direction</span>', '<span>in leadership roles</span>')

# ---------- Réglages ----------
rep('Les réglages qui comptent</h2>', 'The settings that matter</h2>')
rep('<h3>Regrouper par ce que tu veux</h3><p>Secteur, entreprise, fonction, séniorité, année de connexion, ville, formation. Le graphe se reconstruit autour de toi.</p>',
    '<h3>Group by whatever you want</h3><p>Industry, company, function, seniority, year connected, city, education. The graph rebuilds around you.</p>')
rep('<label>Regrouper par</label><div class="sel">Secteur <span aria-hidden="true">⌄</span></div>',
    '<label>Group by</label><div class="sel">Industry <span aria-hidden="true">⌄</span></div>')
rep('<div class="on">Secteur</div><div>Entreprise</div><div class="hv">Fonction</div><div>Séniorité</div><div>Année de connexion</div><div>Ville</div><div>Formation</div>',
    '<div class="on">Industry</div><div>Company</div><div class="hv">Function</div><div>Seniority</div><div>Year connected</div><div>City</div><div>Education</div>')
rep('<h3>Colorer par un autre critère</h3><p>Chaque point prend la couleur de sa séniorité, de sa fonction ou de son année de connexion. La légende donne les comptes.</p>',
    '<h3>Color by another criterion</h3><p>Each dot takes the color of its seniority, its function or the year you connected. The legend gives the counts.</p>')
rep('<span class="lbl">Couleur et grappes&nbsp;: séniorité</span>', '<span class="lbl">Color and clusters: seniority</span>')
rep('<h3>Garder l’essentiel, ou tout voir</h3><p>Le curseur des branches réunit les petits groupes dans «&nbsp;Autres&nbsp;», ou affiche ton réseau entier.</p>',
    '<h3>Keep the essentials, or see it all</h3><p>The branches slider gathers small groups into “Other”, or shows your whole network.</p>')
rep('Branches affichées&nbsp;: <span id="brv">9 sur 28</span>', 'Branches shown: <span id="brv">9 of 28</span>')
rep('>Regroupé par entreprise</p>', '>Grouped by company</p>')
rep('<h3>La fiche complète d’un contact</h3><p>Secteur, fonction, séniorité, ville, formation, date de connexion, et les autres contacts de son entreprise et de son école.</p>',
    '<h3>A contact’s full profile</h3><p>Industry, function, seniority, city, education, connection date, and your other contacts from the same company and school.</p>')
rep('<span>Software Engineer chez Doctolib</span>', '<span>Software Engineer at Doctolib</span>')
rep('<dl><dt>Secteur</dt><dd>Tech &amp; logiciel</dd><dt>Fonction</dt><dd>Tech</dd><dt>Séniorité</dt><dd>Confirmé</dd><dt>Ville</dt><dd>Lyon</dd><dt>Formation</dt><dd>CentraleSupélec</dd><dt>Connectée</dt><dd>en 2019</dd></dl>',
    '<dl><dt>Industry</dt><dd>Tech &amp; software</dd><dt>Function</dt><dd>Tech</dd><dt>Seniority</dt><dd>Mid-level</dd><dt>City</dt><dd>Lyon</dd><dt>Education</dt><dd>CentraleSupélec</dd><dt>Connected</dt><dd>in 2019</dd></dl>')
rep('<p class="ptitle">Aussi chez Doctolib (6)</p>', '<p class="ptitle">Also at Doctolib (6)</p>')
rep('<p class="ptitle">Aussi de CentraleSupélec (3)</p>', '<p class="ptitle">Also from CentraleSupélec (3)</p>')
rep('<h3>Des filtres qui se cumulent</h3><p>Coche juniors et seniors, ajoute un secteur ou une fonction&nbsp;: seuls restent les contacts qui passent tous les filtres.</p>',
    '<h3>Filters that stack up</h3><p>Tick juniors and seniors, add an industry or a function: only the contacts that pass every filter remain.</p>')
rep('<span class="lbl">Séniorité</span>', '<span class="lbl">Seniority</span>')
rep('Confirmé<em>77</em>', 'Mid-level<em>77</em>')
rep('Direction<em>24</em>', 'Director<em>24</em>')
rep('Dirigeant<em>7</em>', 'Executive<em>7</em>')
rep('>24 contacts sur 150</p>', '>24 contacts of 150</p>')
rep('<h3>Tes propres étiquettes</h3><p>Marque un contact comme client, prospect, mentor ou à recontacter, puis regroupe ou filtre par étiquette.</p>',
    '<h3>Your own tags</h3><p>Mark a contact as client, prospect, mentor or to follow up, then group or filter by tag.</p>')
rep('<span>Partenaire</span><span>Mentor</span><span>Recruteur</span><span>À recontacter</span>', '<span>Partner</span><span>Mentor</span><span>Recruiter</span><span>Follow up</span>')

# ---------- Confidentialité ----------
rep('Ce qui quitte ton navigateur</h2>', 'What leaves your browser</h2>')
rep('Aucun serveur ne reçoit ton fichier. Voici tout ce que la page peut envoyer, ligne par ligne.', 'No server receives your file. Here is everything the page can send, line by line.')
rep('<th scope="col">Quoi</th><th scope="col">Envoyé à</th><th scope="col">Quand</th>', '<th scope="col">What</th><th scope="col">Sent to</th><th scope="col">When</th>')
rep('data-l="Envoyé à"', 'data-l="Sent to"', 5)
rep('data-l="Quand"', 'data-l="When"', 5)
rep('<td>Tes contacts&nbsp;: noms, profils, emails</td>', '<td>Your contacts: names, profiles, emails</td>')
rep('class="never">Personne</td>', 'class="never">Nobody</td>')
rep('class="never">Jamais</td>', 'class="never">Never</td>')
rep('<td>Le domaine des entreprises, par exemple doctolib.fr</td>', '<td>Company domains, for example doctolib.fr</td>')
rep('>Brandfetch, pour les logos</td>', '>Brandfetch, for the logos</td>')
rep('>Tant que l’option Logos est cochée. Elle l’est par défaut et se décoche en un clic.</td>', '>As long as the Logos option is ticked. It is by default, and unticks in one click.</td>')
rep('<td>Des noms d’entreprises et intitulés de poste non reconnus</td>', '<td>Company names and job titles that weren’t recognized</td>')
rep('>L’IA que tu choisis, avec ta propre clé</td>', '>The AI you choose, with your own key</td>')
rep('>Seulement si tu lances le classement par IA</td>', '>Only if you run the AI classification</td>')
rep('<td>Tes corrections de classement</td>', '<td>Your classification corrections</td>')
rep('>Le dictionnaire partagé de Synapses</td>', '>Synapses’ shared dictionary</td>')
rep('>Seulement si tu coches «&nbsp;Partager mes corrections&nbsp;»</td>', '>Only if you tick “Share my corrections”</td>')
rep('<td>+1 au compteur de réseaux visualisés</td>', '<td>+1 on the counter of mapped networks</td>')
rep('>Un compteur anonyme</td>', '>An anonymous counter</td>')
rep('>Après un import, au plus une fois par jour</td>', '>After an import, at most once a day</td>')

# ---------- Questions ----------
rep('<h2 id="questions-titre" class="rise">Questions</h2>', '<h2 id="questions-titre" class="rise">Questions</h2>')
rep('C’est vraiment gratuit&nbsp;?<span', 'Is it really free?<span')
rep('<p>Oui. Pas de compte, pas d’abonnement, pas de publicité. Seul le classement par IA, facultatif, utilise ta propre clé chez le fournisseur que tu choisis.</p>',
    '<p>Yes. No account, no subscription, no ads. Only the optional AI classification uses your own key, with the provider you choose.</p>')
rep('Synapses est-il lié à LinkedIn&nbsp;?<span', 'Is Synapses linked to LinkedIn?<span')
rep('<p>Non. C’est un outil indépendant, non affilié à LinkedIn. Il ne se connecte pas à ton compte&nbsp;: il lit seulement l’export que tu télécharges.</p>',
    '<p>No. It’s an independent tool, not affiliated with LinkedIn. It doesn’t connect to your account: it only reads the export you download.</p>')
rep('Combien de temps pour avoir l’export&nbsp;?<span', 'How long does the export take?<span')
rep('<p>La demande prend deux minutes. L’archive des relations arrive par email, en général une dizaine de minutes plus tard.</p>',
    '<p>Requesting it takes two minutes. The connections archive arrives by email, usually about ten minutes later.</p>')
rep('Et si un secteur est mal deviné&nbsp;?<span', 'What if an industry is guessed wrong?<span')
rep('<p>Secteur, fonction et séniorité sont estimés. Corrige-les dans la fiche du contact&nbsp;: la correction s’applique à toute l’entreprise ou à tout l’intitulé de poste. Tu peux aussi affiner avec une IA, avec ta clé.</p>',
    '<p>Industry, function and seniority are estimates. Correct them in the contact’s profile: the correction applies to the whole company or job title. You can also refine them with an AI, using your own key.</p>')
rep('Je peux essayer sans mon export&nbsp;?<span', 'Can I try it without my export?<span')
rep('<p>Oui. La démo s’ouvre directement sur un réseau fictif de 150 contacts, avec toutes les fonctions.</p>',
    '<p>Yes. The demo opens straight onto a fictional network of 150 contacts, with every feature.</p>')
rep('Et sur téléphone&nbsp;?<span', 'What about on a phone?<span')
rep('<p>Le graphe s’adapte à l’écran, et une vue Liste reprend tout en texte. Pour récupérer et déposer l’archive, l’ordinateur reste plus pratique.</p></details>',
    '<p>The graph adapts to the screen, and a List view shows everything as text. To get and drop the archive, a computer is still easier.</p></details>\n'
    '        <details name="faq" class="rise" style="--i:6"><summary>Is the tool in English?<span class="pm" aria-hidden="true"></span></summary><p>Not yet: its interface is in French for now, and an English version is planned. Your export works the same, and English job titles are recognized.</p></details>')

# ---------- Fin et pied de page ----------
rep('Ouvre <a class="go" href="app/">la démo</a> ou <a class="alt" href="app/#importer">ton export</a>', 'Open <a class="go" href="app/">the demo</a> or <a class="alt" href="app/#importer">your export</a>')
rep('<p>La démo tourne sur 150 contacts fictifs. Ton export, lui, reste dans ton navigateur.</p>', '<p>The demo runs on 150 fictional contacts. Your export stays in your browser.</p>')
rep('<p>Synapses lit ton export LinkedIn dans ton navigateur et en fait une carte de ton réseau.</p>', '<p>Synapses reads your LinkedIn export in your browser and turns it into a map of your network.</p>')
rep('Outil indépendant, non affilié à LinkedIn.<br>Voix de la vidéo&nbsp;: ElevenLabs.', 'Independent tool, not affiliated with LinkedIn.<br>Video voice: ElevenLabs.')
rep('aria-label="Pied de page"', 'aria-label="Footer"')
rep('<a href="app/">Ouvrir l’outil</a>', '<a href="app/">Open the tool</a>')
rep('<p>Conçu et développé par <a', '<p>Designed and built by <a')
rep('Product Manager, avec Claude Code.</p><p>Le code est public&nbsp;: <a', 'Product Manager, with Claude Code.</p><p>The code is public: <a')
rep('<b>Essayer la démo</b>', '<b>Try the demo</b>')

# ---------- Script : réseau de démo et textes générés ----------
EN = {
    # secteurs
    'Conseil': 'Consulting', 'Banque & assurance': 'Banking & insurance', 'Santé': 'Healthcare', 'Retail & conso': 'Retail & consumer',
    'Tech & logiciel': 'Tech & software', 'Télécom & médias': 'Telecom & media', 'Transport & mobilité': 'Transport & mobility',
    'Énergie & industrie': 'Energy & industry', 'Secteur public & éducation': 'Public sector & education', 'Non classé': 'Unclassified',
    # fonctions
    'Produit': 'Product', 'Direction générale': 'General management', 'Opérations': 'Operations', 'RH': 'HR',
    # séniorité
    'Confirmé': 'Mid-level', 'Direction': 'Director', 'Dirigeant': 'Executive',
    # postes
    'Directeur commercial': 'Sales Director', 'Développeur full-stack': 'Full-stack Developer', 'Stagiaire produit': 'Product Intern',
    'Consultant senior': 'Senior Consultant', 'Contrôleur de gestion': 'Financial Controller', 'Directeur des opérations': 'Operations Director',
    'Responsable marketing': 'Marketing Manager', 'Chargée de recrutement': 'Recruiter', 'Directrice financière': 'Finance Director',
    'Alternant data': 'Data Apprentice', 'Manager conseil': 'Consulting Manager', 'Chef de projet digital': 'Digital Project Manager',
    'Analyste financier': 'Financial Analyst', 'CEO & co-fondateur': 'CEO & Co-founder',
}
js_en = 'const EN = {' + ','.join(f'{k!r}:{v!r}' for k, v in EN.items()) + '};'
js_en = js_en.replace("'", '"')
rep('  /* Réseau de démonstration de l’outil : 150 contacts fictifs',
    '  /* Version anglaise : les secteurs, fonctions, séniorités et postes du réseau de démo sont traduits ici */\n  ' + js_en + '\n  /* Réseau de démonstration de l’outil : 150 contacts fictifs')
rep('.map(([n, co, pos, sec, fn, sen]) => ({n, co, pos, sec, fn, sen}));',
    '.map(([n, co, pos, sec, fn, sen]) => ({n, co, pos:EN[pos] || pos, sec:EN[sec] || sec, fn:EN[fn] || fn, sen:EN[sen] || sen}));')
rep("const SEN = ['Junior','Confirmé','Senior','Manager','Direction','Dirigeant'];", "const SEN = ['Junior','Mid-level','Senior','Manager','Director','Executive'];")
rep('const pct = (n, t) => `${Math.round(n / t * 100)}\u00a0%`;', 'const pct = (n, t) => `${Math.round(n / t * 100)}%`;')
rep("let by = 'sen', selected = 'Tech & logiciel';", "let by = 'sen', selected = 'Tech & software';")
rep(".textContent = 'Moi';", ".textContent = 'Me';")
rep('${list.length} contacts, soit ${pct(list.length, DEMO.length)} du réseau', '${list.length} contacts, ${pct(list.length, DEMO.length)} of the network')
rep('`<p class="sub">et ${list.length - 6} autres</p>`', '`<p class="sub">and ${list.length - 6} more</p>`')
rep("+br.value >= 28 ? 'toutes (28)' : `${br.value} sur 28`", "+br.value >= 28 ? 'all (28)' : `${br.value} of 28`")
rep("c.sec === 'Banque & assurance'", "c.sec === 'Banking & insurance'")
rep("n <= 8 ? 'à développer' : ''", "n <= 8 ? 'to grow' : ''")
rep("c.sen === 'Direction' || c.sen === 'Dirigeant'", "c.sen === 'Director' || c.sen === 'Executive'")
rep("e.innerHTML = `<strong>${n.toLocaleString('fr-FR')}</strong> réseaux déjà visualisés`;", "e.innerHTML = `<strong>${n.toLocaleString('en-US')}</strong> networks already mapped`;")
rep("flap.setAttribute('aria-label', `${n.toLocaleString('fr-FR')} réseaux`);", "flap.setAttribute('aria-label', `${n.toLocaleString('en-US')} networks`);")

if missing:
    sys.exit('Phrases introuvables dans index.html, à mettre à jour dans outils/landing-en.py :\n- ' + '\n- '.join(missing))

# ---------- Chemins : la page est servie depuis en/ ----------
s = re.sub(r'(?<=["\s,(])(assets/|app/|favicon\.svg|apple-touch-icon\.png)', r'../\1', s)

out = ROOT / 'en' / 'index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(s, encoding='utf-8')
print(f'{out.relative_to(ROOT)} écrit')
