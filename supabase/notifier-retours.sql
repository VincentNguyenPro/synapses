-- Synapses : copie de chaque nouvel avis par email (choix de Vincent du 12 novembre 2026)
-- À exécuter dans Supabase › SQL Editor, après supabase/retours.sql. Le script peut être relancé sans risque.
--
-- Principe : à chaque avis enregistré, la base appelle le script Google Apps Script du compte
-- contact.synapses.app@gmail.com (supabase/notifier-retours.gs), qui envoie le mail à cette boîte.
-- L’URL du script et le jeton secret sont gardés dans le coffre de Supabase (Vault), jamais dans ce dépôt public.
-- Si l’envoi échoue, l’avis est quand même enregistré.
--
-- Une seule fois, avant ce script (remplacer les deux valeurs, ne pas les commiter) :
--   select vault.create_secret('https://script.google.com/macros/s/…/exec', 'retours_url');
--   select vault.create_secret('LE_JETON_DU_SCRIPT', 'retours_jeton');
-- Pour les changer plus tard :
--   select vault.update_secret((select id from vault.secrets where name = 'retours_url'), 'nouvelle URL');

create extension if not exists pg_net with schema extensions;

create or replace function public.notifier_retour()
returns trigger
language plpgsql security definer set search_path = public, extensions as $$
declare u text; j text;
begin
  select decrypted_secret into u from vault.decrypted_secrets where name = 'retours_url';
  select decrypted_secret into j from vault.decrypted_secrets where name = 'retours_jeton';
  if u is null or j is null then return new; end if;
  perform net.http_post(
    url := u,
    body := jsonb_build_object('jeton', j, 'retour', jsonb_build_object(
      'id', new.id, 'note', new.note, 'message', new.message, 'email', new.email, 'page', new.page, 'langue', new.langue)),
    headers := '{"Content-Type": "application/json"}'::jsonb,
    timeout_milliseconds := 10000);
  return new;
exception when others then
  return new;  -- jamais bloquer l’enregistrement d’un avis
end;
$$;

revoke all on function public.notifier_retour() from public, anon, authenticated;

drop trigger if exists retour_notifie on public.retours;
create trigger retour_notifie after insert on public.retours
  for each row execute function public.notifier_retour();
