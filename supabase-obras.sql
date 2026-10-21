-- ============================================
-- MÚLTIPLAS OBRAS — rode UMA VEZ no Supabase
-- Supabase > SQL Editor > New query > cole tudo > Run
-- ============================================
-- A Casa Caio continua nas tabelas antigas (compras, mao_de_obra, ...).
-- As obras novas ficam nesta tabela, cada uma com o seu pacote de dados.

create table if not exists obras (
  id text primary key,
  nome text not null,
  local text,
  area numeric,
  valor_m2 numeric,
  dados jsonb not null default '{}'::jsonb,
  atualizado_em timestamptz default now()
);

alter table obras enable row level security;

do $$
begin
  if not exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'obras' and policyname = 'obras_all'
  ) then
    create policy obras_all on obras for all using (true) with check (true);
  end if;
end $$;

grant all on table obras to anon, authenticated;
