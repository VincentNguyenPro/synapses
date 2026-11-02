-- Synapses : base partagée du dictionnaire de classification (Supabase / PostgreSQL)
-- À exécuter une fois dans Supabase › SQL Editor. Le script peut être relancé sans risque.
--
-- Principe :
--   • data/entreprises.json et data/postes.json (dans le dépôt) restent le dictionnaire de base.
--   • dict_entreprises et dict_postes : ajouts validés, lisibles par tous, qui complètent les JSON.
--   • contributions : propositions envoyées par les visiteurs (corrections manuelles ou classement par LLM),
--     sans aucun nom de personne. Le public peut seulement en ajouter, jamais les lire ni les modifier.
--   • Une contribution passe dans le dictionnaire quand son statut devient « validee » (dans Table Editor).

-- ---------- Libellés autorisés (doivent correspondre à data/*.json) ----------
create or replace function public.secteur_valide(s text) returns boolean language sql immutable as $$
  select s = any (array['Agroalimentaire','Banque & assurance','Conseil','Finance & investissement',
    'Immobilier & construction','Juridique','Retail & conso','Santé','Secteur public & éducation',
    'Tech & logiciel','Tourisme, hôtellerie & restauration','Transport & mobilité','Télécom & médias',
    'Énergie & industrie'])
$$;
create or replace function public.fonction_valide(f text) returns boolean language sql immutable as $$
  select f = any (array['Direction générale','Produit','Data','Tech','Sales','Marketing','Finance','RH',
    'Juridique','Enseignement & recherche','Conseil','Opérations','Autre'])
$$;
create or replace function public.seniorite_valide(n text) returns boolean language sql immutable as $$
  select n = any (array['Junior','Confirmé','Senior','Manager','Direction','Dirigeant'])
$$;

-- ---------- Dictionnaire validé ----------
create table if not exists public.dict_entreprises (
  cle      text primary key check (char_length(cle) between 1 and 120),
  nom      text not null check (char_length(nom) between 1 and 150),
  secteur  text not null check (public.secteur_valide(secteur)),
  source   text not null default 'contribution',
  maj      timestamptz not null default now()
);
create table if not exists public.dict_postes (
  cle       text primary key check (char_length(cle) between 1 and 120),
  intitule  text not null check (char_length(intitule) between 1 and 150),
  fonction  text not null check (public.fonction_valide(fonction)),
  seniorite text not null check (public.seniorite_valide(seniorite)),
  source    text not null default 'contribution',
  maj       timestamptz not null default now()
);

-- ---------- Propositions des visiteurs ----------
create table if not exists public.contributions (
  id        bigint generated always as identity primary key,
  type      text not null check (type in ('entreprise','poste')),
  cle       text not null check (char_length(cle) between 1 and 120),
  libelle   text not null check (char_length(libelle) between 1 and 150),
  secteur   text check (secteur is null or public.secteur_valide(secteur)),
  fonction  text check (fonction is null or public.fonction_valide(fonction)),
  seniorite text check (seniorite is null or public.seniorite_valide(seniorite)),
  origine   text not null check (origine in ('correction','llm')),
  modele    text check (modele is null or char_length(modele) <= 60),
  statut    text not null default 'en_attente' check (statut in ('en_attente','validee','refusee')),
  cree_le   timestamptz not null default now(),
  check ((type = 'entreprise' and secteur is not null and fonction is null and seniorite is null)
      or (type = 'poste' and secteur is null and fonction is not null and seniorite is not null))
);
create index if not exists contributions_attente on public.contributions (statut, type, cle);

-- ---------- Validation : une contribution validée entre dans le dictionnaire ----------
create or replace function public.appliquer_contribution() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.statut = 'validee' and (tg_op = 'INSERT' or old.statut is distinct from 'validee') then
    if new.type = 'entreprise' then
      insert into dict_entreprises (cle, nom, secteur, source)
      values (new.cle, new.libelle, new.secteur, new.origine)
      on conflict (cle) do update set secteur = excluded.secteur, nom = excluded.nom, source = excluded.source, maj = now();
    else
      insert into dict_postes (cle, intitule, fonction, seniorite, source)
      values (new.cle, new.libelle, new.fonction, new.seniorite, new.origine)
      on conflict (cle) do update set fonction = excluded.fonction, seniorite = excluded.seniorite,
        intitule = excluded.intitule, source = excluded.source, maj = now();
    end if;
  end if;
  return new;
end $$;
drop trigger if exists contributions_validees on public.contributions;
create trigger contributions_validees after insert or update of statut on public.contributions
  for each row execute function public.appliquer_contribution();

-- ---------- Vue de modération (non exposée au public) ----------
-- Regroupe les propositions identiques : plus « nb » est élevé, plus la proposition est fiable.
create or replace view public.a_valider as
  select type, cle, min(libelle) as libelle, secteur, fonction, seniorite,
         count(*) as nb, count(*) filter (where origine = 'correction') as nb_corrections,
         min(cree_le) as premiere, max(cree_le) as derniere
  from public.contributions where statut = 'en_attente'
  group by type, cle, secteur, fonction, seniorite
  order by nb desc, derniere desc;

-- Valide d’un coup toutes les propositions en attente proposées au moins « seuil » fois
-- (à lancer dans SQL Editor, par exemple : select public.valider_consensus(3);)
create or replace function public.valider_consensus(seuil int default 3) returns int
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  with ok as (
    select type, cle, secteur, fonction, seniorite from contributions where statut = 'en_attente'
    group by type, cle, secteur, fonction, seniorite having count(*) >= seuil
  )
  update contributions c set statut = 'validee' from ok
  where c.statut = 'en_attente' and c.type = ok.type and c.cle = ok.cle
    and c.secteur is not distinct from ok.secteur and c.fonction is not distinct from ok.fonction
    and c.seniorite is not distinct from ok.seniorite;
  get diagnostics n = row_count;
  return n;
end $$;

-- ---------- Droits d’accès du public (clé publishable = rôle anon) ----------
alter table public.dict_entreprises enable row level security;
alter table public.dict_postes enable row level security;
alter table public.contributions enable row level security;

revoke all on public.dict_entreprises, public.dict_postes, public.contributions, public.a_valider from anon, authenticated;
revoke all on function public.valider_consensus(int), public.appliquer_contribution() from public, anon, authenticated;

-- Lecture du dictionnaire validé
grant select on public.dict_entreprises, public.dict_postes to anon, authenticated;
drop policy if exists lecture_publique on public.dict_entreprises;
create policy lecture_publique on public.dict_entreprises for select to anon, authenticated using (true);
drop policy if exists lecture_publique on public.dict_postes;
create policy lecture_publique on public.dict_postes for select to anon, authenticated using (true);

-- Ajout de propositions uniquement : colonnes limitées, statut forcé à « en_attente », aucune lecture
grant insert (type, cle, libelle, secteur, fonction, seniorite, origine, modele) on public.contributions to anon, authenticated;
drop policy if exists proposer on public.contributions;
create policy proposer on public.contributions for insert to anon, authenticated with check (statut = 'en_attente');
