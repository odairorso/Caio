# Obra Fácil — Caio

App de gestão financeira da obra, com gráficos, parcelas automáticas e sincronização em nuvem.

## 🚀 Deploy no Vercel

1. Acesse [vercel.com](https://vercel.com) e faça login com GitHub
2. Clique em **"Add New"** → **"Project"**
3. Arraste a pasta `App Caio` ou conecte o repositório Git
4. Clique em **"Deploy"** — pronto! Vai gerar um link tipo `obra-facil.vercel.app`

## ☁️ Configurar Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta grátis
2. Clique em **"New Project"** e dê um nome (ex: `obra-facil`)
3. Aguarde criar e vá em **SQL Editor** (menu lateral)
4. Cole todo o conteúdo do arquivo `supabase-schema.sql` e clique em **"Run"**
5. Vá em **Project Settings** → **API** e copie:
   - **Project URL** (ex: `https://xxxx.supabase.co`)
   - **anon public** key
6. Abra o `index.html` e procure por estas linhas no início do JavaScript:
   ```js
   const SUPABASE_URL='SUA_URL_SUPABASE';
   const SUPABASE_KEY='SUA_ANON_KEY_SUPABASE';
   ```
7. Substitua pelos seus valores reais
8. Suba o arquivo atualizado para o Vercel (arraste de novo)

## 📱 Recursos

- 📊 Dashboard com gráficos
- 🧱 243 compras de material
- 👷 34 pagamentos de mão de obra
- 📋 30 serviços de documentação
- 💳 Parcelas automáticas do cartão
- 🏦 Financiamento + contas da obra
- 🤝 Rateio com Matheus
- ☁️ Sync com Supabase
- 📥 Exportar CSV
- 📱 Otimizado para celular

## 🛠️ Tecnologias

- HTML + JavaScript vanilla
- Chart.js (gráficos)
- Supabase (banco de dados)
- Vercel (hospedagem)
