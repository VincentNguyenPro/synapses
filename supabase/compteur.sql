-- Synapses : compteur anonyme des réseaux visualisés (Supabase / PostgreSQL)
-- À exécuter une fois dans Supabase › SQL Editor. Le script peut être relancé sans risque (il ne remet pas le total à zéro).
--
-- Principe :
--   • une seule ligne, un seul nombre : le total des imports réussis ;
--   • la page appelle compter_soumission() après un import (au plus une fois par jour et par navigateur) :
--     aucune donnée n’est envoyée, ni fichier, ni nom, ni entreprise ;
--   • le public peut lire le total et l’augmenter de 1, rien d’autre.

create table if not exists public.compteur (
  id    int primary key default 1 check (id = 1),
  total bigint not null default 0,
  maj   timestamptz not null default now()
);
insert into public.compteur (id, total) values (1, 0) on conflict (id) do nothing;

-- +1, et renvoie le nouveau total
create or replace function public.compter_soumission() returns bigint
language sql security definer set search_path = public as $$
  update compteur set total = total + 1, maj = now() where id = 1 returning total;
$$;

-- Droits du public (clé publishable = rôle anon) : lire le total, appeler +1
alter table public.compteur enable row level security;
revoke all on public.compteur from anon, authenticated;
grant select (total) on public.compteur to anon, authenticated;
drop policy if exists lecture_publique on public.compteur;
create policy lecture_publique on public.compteur for select to anon, authenticated using (true);

revoke all on function public.compter_soumission() from public, anon, authenticated;
grant execute on function public.compter_soumission() to anon, authenticated;
