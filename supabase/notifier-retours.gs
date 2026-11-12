// Synapses : copie de chaque avis par email, dans la boîte contact.synapses.app@gmail.com (choix de Vincent du 12 novembre 2026)
// Script Google Apps Script du compte contact.synapses.app@gmail.com (script.google.com, connecté à ce compte).
// Appelé par la base Supabase (supabase/notifier-retours.sql) à chaque nouvel avis ; il envoie le mail à son propre compte.
// Aucun mot de passe n’est stocké nulle part : seul un jeton secret, gardé dans les propriétés du script (jamais dans ce fichier)
// et dans le coffre de Supabase (Vault), prouve que l’appel vient bien de la base.
//
// Mise en place :
//   1. script.google.com › Nouveau projet « Synapses avis » ; coller ce fichier à la place de Code.gs ; enregistrer.
//   2. Paramètres du projet › Propriétés du script › ajouter JETON = une longue chaîne aléatoire (la même que dans Supabase).
//   3. Déployer › Nouveau déploiement › Type « Application Web » ; Exécuter en tant que « Moi » ; Accès « Tout le monde » ;
//      autoriser l’envoi de mails ; copier l’URL qui finit par /exec (à mettre dans Supabase, jamais dans le dépôt).
//   4. Déclencheurs (icône réveil) › Ajouter › fonction « purger », source « Déclencheur temporel », chaque jour :
//      les mails d’avis de plus de 24 mois partent à la corbeille, comme dans la base (promis sur la page legal/).

function doPost(e) {
  const jeton = PropertiesService.getScriptProperties().getProperty('JETON');
  let d = {};
  try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { return texte('illisible'); }
  if (!jeton || d.jeton !== jeton) return texte('refusé');
  const r = d.retour || {};
  const message = String(r.message || '').slice(0, 2000);
  if (!message) return texte('vide');
  const email = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(r.email || '') ? r.email : '';
  const note = r.note ? `${r.note}/5` : 'pas de note';
  const corps = [
    message,
    '',
    '—',
    `Note : ${note}`,
    `Page : ${r.page === 'landing' ? 'page d’accueil' : 'outil'} (${r.langue === 'en' ? 'anglais' : 'français'})`,
    email ? `Réponse souhaitée à : ${email} (bouton Répondre)` : 'Pas de réponse demandée',
    `Avis n° ${r.id} dans Supabase › Table Editor › retours`,
  ].join('\n');
  const opts = { name: 'Synapses', body: corps };
  if (email) opts.replyTo = email;
  MailApp.sendEmail(Object.assign({
    to: Session.getEffectiveUser().getEmail(),
    subject: `Avis Synapses${r.note ? ' ' + r.note + '/5' : ''} : ${message.replace(/\s+/g, ' ').slice(0, 60)}`,
  }, opts));
  return texte('ok');
}

// Mails d’avis de plus de 24 mois : à la corbeille (vidée par Gmail après 30 jours)
function purger() {
  GmailApp.search('subject:"Avis Synapses" older_than:2y').forEach(t => t.moveToTrash());
}

function texte(t) { return ContentService.createTextOutput(t); }
