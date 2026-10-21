# Obra Fácil — Casa Caio

Controle de custos da obra da Casa Caio: compras, parcelas do cartão, mão de obra,
documentação, financiamento, juros e rateio com o Matheus.

- **No ar:** https://caio-nine-nu.vercel.app/
- **Funciona sem internet** (PWA instalável no celular)
- **Sincroniza entre aparelhos** pelo Supabase

---

## ⚠️ Leia antes de mexer

O `index.html` é **gerado**. Não edite ele na mão: qualquer alteração é perdida na
próxima geração.

| Arquivo | Papel |
|---|---|
| `_build/gen_app3.py` | **Fonte de verdade do app.** Todo ajuste de tela, texto ou lógica vai aqui. |
| `index.html` | Produto gerado (é o que o navegador carrega). Não editar. |
| `obra_data.json` | Dados extraídos da planilha. |
| `_build/testes.cjs` | Testes de comportamento (datas, parcelas, sincronização). |
| `_build/verificar.cjs` | Confere contagens, somas e sintaxe. |
| `sw.js` / `manifest.webmanifest` | Fazem o app funcionar offline e ser instalável. |

### Como alterar o app

```bash
python _build/gen_app3.py     # gera o index.html
node _build/verificar.cjs     # confere dados e sintaxe
node _build/testes.cjs        # confere o comportamento
git add -A && git commit -m "..." && git push
```

O Vercel publica sozinho ~1 minuto depois do push.

**Só publique se os dois comandos de verificação passarem.** O `verificar.cjs`
sozinho não pega erro de lógica — ele só conta registros e valida sintaxe.

---

## 📊 O que tem dentro

- Painel com total investido, gráficos e alerta de parcelas atrasadas
- 243 compras de material
- 32 pagamentos de mão de obra (R$ 62.007,32)
- 30 serviços de documentação
- Parcelas automáticas do cartão (vencidas aparecem como **atrasadas**)
- Financiamento, juros e contas da obra
- Rateio com o Matheus
- Backup completo em JSON (botão ⬇️ no topo)
- Exportação CSV

---

## ☁️ Supabase

Projeto: `nvzqjvltzhmbtbtwletv.supabase.co`

A sincronização é **automática**: ao abrir, o app puxa o que está na nuvem e mescla
com o que está no aparelho. Não existem botões de "enviar" ou "baixar".

- Se o aparelho estiver sem internet, os dados continuam salvos e são enviados depois.
- O ícone de nuvem no topo mostra o estado: ☁️ sincronizado · 📴 sem internet · ⚠️ falha.
- O plano grátis do Supabase pausa após 7 dias sem uso. O workflow
  `.github/workflows/keep-alive.yml` faz uma consulta diária (9h de Brasília) para evitar isso.

### 🔒 Segurança — decisão de 21/10/2026: manter aberto por enquanto

Hoje o banco aceita leitura e escrita de qualquer pessoa que tenha o link do app
(as políticas do `supabase-schema.sql` são `FOR ALL USING (true)` e a chave pública
está no HTML). Isso foi avaliado e, por decisão do responsável, **ficou assim por
enquanto**: o link não é divulgado, então o risco na prática é baixo.

Se um dia quiser fechar de verdade, o caminho é:

1. Ativar login por e-mail e senha no Supabase e criar um usuário.
2. Trocar as políticas por `USING (auth.role() = 'authenticated')` no
   `supabase-schema.sql`.
3. Adicionar a tela de login no `_build/gen_app3.py`.

Não adianta apenas esconder a chave no HTML: a chave pública é, por definição,
visível para quem abre o app. A proteção real vem das políticas (RLS).

---

## 📱 Instalar no celular

1. Abra https://caio-nine-nu.vercel.app/ no Chrome (Android) ou Safari (iPhone)
2. Menu → **"Adicionar à tela de início"**
3. O app abre em tela cheia, inclusive sem internet

---

## 🗄️ Sobre o app React antigo

Até outubro/2026 existia nesta pasta um app React/TanStack (gerado pelo Lovable) em
`src/`, com outro banco local (`obra-facil-v1`) e sem Supabase. Ele **nunca foi
publicado**: não estava no Git e o Vercel sempre serviu o `index.html`.

Ele foi movido para `Documents\App Caio - app React arquivado (nao usar)`.
Não é necessário para nada e não deve voltar para esta pasta.
