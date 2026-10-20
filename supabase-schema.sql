-- ============================================
-- SCHEMA: Obra Fácil — Casa Caio
-- Cole este arquivo no Supabase SQL Editor
-- ============================================

-- Tabela: compras (materiais)
CREATE TABLE IF NOT EXISTS compras (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  quantidade TEXT,
  material TEXT NOT NULL,
  valor NUMERIC(12,2) NOT NULL DEFAULT 0,
  forma TEXT NOT NULL DEFAULT 'dinheiro',
  parcelas INTEGER NOT NULL DEFAULT 1,
  fornecedor TEXT,
  data DATE,
  pagador TEXT DEFAULT 'CAIO',
  status TEXT NOT NULL DEFAULT 'pago',
  categoria TEXT NOT NULL DEFAULT 'Outros',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela: mao_de_obra (pagamentos de mão de obra)
CREATE TABLE IF NOT EXISTS mao_de_obra (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  data DATE,
  valor NUMERIC(12,2) NOT NULL DEFAULT 0,
  descricao TEXT,
  status TEXT NOT NULL DEFAULT 'pago',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela: documentos (serviços de documentação)
CREATE TABLE IF NOT EXISTS documentos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  servico TEXT NOT NULL,
  valor NUMERIC(12,2) NOT NULL DEFAULT 0,
  data DATE,
  forma TEXT,
  obs TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela: parcelas_pagas (controle de parcelas do cartão quitadas)
CREATE TABLE IF NOT EXISTS parcelas_pagas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  parcela_id TEXT NOT NULL UNIQUE,
  paga_em TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela: juros (parcelas do financiamento)
CREATE TABLE IF NOT EXISTS juros (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  data DATE,
  valor NUMERIC(12,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela: contas (água, luz, IPTU)
CREATE TABLE IF NOT EXISTS contas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  item TEXT NOT NULL,
  mes TEXT,
  valor NUMERIC(12,2) NOT NULL DEFAULT 0,
  status TEXT DEFAULT 'PAGO',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- RLS (Row Level Security) — Habilitar acesso anônimo
-- Para app pessoal, permite leitura/escrita sem login
-- ============================================

ALTER TABLE compras ENABLE ROW LEVEL SECURITY;
ALTER TABLE mao_de_obra ENABLE ROW LEVEL SECURITY;
ALTER TABLE documentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE parcelas_pagas ENABLE ROW LEVEL SECURITY;
ALTER TABLE juros ENABLE ROW LEVEL SECURITY;
ALTER TABLE contas ENABLE ROW LEVEL SECURITY;

-- Policies: acesso total para anônimo (app pessoal)
CREATE POLICY "acesso_total_compras" ON compras FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "acesso_total_mao_de_obra" ON mao_de_obra FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "acesso_total_documentos" ON documentos FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "acesso_total_parcelas_pagas" ON parcelas_pagas FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "acesso_total_juros" ON juros FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "acesso_total_contas" ON contas FOR ALL USING (true) WITH CHECK (true);

-- ============================================
-- ÍNDICES para performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_compras_data ON compras(data);
CREATE INDEX IF NOT EXISTS idx_compras_fornecedor ON compras(fornecedor);
CREATE INDEX IF NOT EXISTS idx_compras_categoria ON compras(categoria);
CREATE INDEX IF NOT EXISTS idx_mao_de_obra_data ON mao_de_obra(data);
CREATE INDEX IF NOT EXISTS idx_documentos_data ON documentos(data);
CREATE INDEX IF NOT EXISTS idx_juros_data ON juros(data);
CREATE INDEX IF NOT EXISTS idx_contas_mes ON contas(mes);
