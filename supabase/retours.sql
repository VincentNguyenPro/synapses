-- Synapses : retours des utilisateurs (« Donner mon avis »), Supabase / PostgreSQL, projet UE
-- À exécuter une fois dans Supabase › SQL Editor. Le script peut être relancé sans risque.
--
-- Principe (choix de Vincent du 4 novembre 2026) :
--   • l’outil et la landing page envoient un avis seulement quand l’utilisateur clique sur « Envoyer » ;
--   • partent : le message, une note de 1 à 5 (facultative), l’email seulement si la personne veut une réponse,
--     la page d’où elle écrit (« outil » ou « landing ») et la langue de la page ; rien d’autre, jamais le réseau ;
--   • le public peut seulement appeler envoyer_retour() : il ne peut ni lire, ni modifier, ni supprimer un retour ;
--   • Vincent lit les retours dans Supabase › Table Editor › retours, et suit leur traitement avec la colonne statut ;
--   • les retours de plus de 24 mois sont supprimés automatiquement (tâche « purger-retours », en bas du fichier).

create table if not exists public.retours (
  id       bigint generated always as identity primary key,
  cree_le  timestamptz not null default now(),
  note     smallint check (note between 1 and 5),
  message  text not null check (char_length(message) between 3 and 2000),
  email    text check (email is null or (char_length(email) <= 200 and email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$')),
  page     text not null check (page in ('outil', 'landing')),
  langue   text not null default 'fr' check (langue in ('fr', 'en')),
  statut   text not null default 'nouveau' check (statut in ('nouveau', 'lu', 'prevu', 'fait', 'ecarte')),
  reponse  text   -- note de Vincent : ce qui a été fait ou répondu
);

-- Envoi d’un retour. Garde-fou contre les envois en rafale : au plus 30 retours en 10 minutes, tous visiteurs confondus.
create or replace function public.envoyer_retour(p_message text, p_note smallint default null, p_email text default null,
                                                 p_page text default 'outil', p_langue text default 'fr')
returns void
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from retours where cree_le > now() - interval '10 minutes') >= 30 then
    raise exception 'trop de retours, réessaie dans quelques minutes';
  end if;
  insert into retours (message, note, email, page, langue)
  values (btrim(p_message), p_note, nullif(btrim(coalesce(p_email, '')), ''), p_page, p_langue);
end;
$$;

-- Droits du public (clé publishable = rôle anon) : aucun accès à la table, seulement la fonction d’envoi
alter table public.retours enable row level security;
revoke all on public.retours from anon, authenticated;
revoke all on function public.envoyer_retour(text, smallint, text, text, text) from public, anon, authenticated;
grant execute on function public.envoyer_retour(text, smallint, text, text, text) to anon, authenticated;

-- Purge automatique (choix de Vincent du 5 novembre 2026, promis sur la page legal/) : chaque nuit à 3 h 15 (UTC),
-- les retours de plus de 24 mois sont supprimés, email compris. Tâche pg_cron, visible dans Supabase › Integrations › Cron.
create extension if not exists pg_cron with schema pg_catalog;
select cron.unschedule(jobid) from cron.job where jobname = 'purger-retours';
select cron.schedule('purger-retours', '15 3 * * *',
  $$delete from public.retours where cree_le < now() - interval '24 months'$$);

-- Fait voir la nouvelle table et la fonction à l’API tout de suite
notify pgrst, 'reload schema';
