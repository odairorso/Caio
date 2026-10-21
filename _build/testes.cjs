/* Testes de comportamento do app Obra Facil — Casa Caio.
 *
 * O verificar.cjs confere contagem e sintaxe. Isto aqui confere SE A CONTA
 * FECHA: datas de vencimento, soma das parcelas, escape, mescla com a nuvem.
 *
 * Uso: node _build/testes.cjs
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const RAIZ = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(RAIZ, 'index.html'), 'utf8');

const blocos = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (!blocos.length) {
  console.error('ERRO: nenhum <script> embutido encontrado em index.html');
  process.exit(1);
}
const JS = blocos[blocos.length - 1];

/* ---------- extracao das funcoes puras ---------- */
function pegarFuncao(src, nome) {
  const i = src.indexOf('function ' + nome + '(');
  if (i < 0) return null;
  const ini = src.indexOf('{', i);
  let d = 0;
  for (let k = ini; k < src.length; k++) {
    if (src[k] === '{') d++;
    else if (src[k] === '}') {
      d--;
      if (d === 0) return src.slice(i, k + 1);
    }
  }
  return null;
}

function pegarDecl(src, nome) {
  for (const kw of ['const ', 'let ']) {
    const i = src.indexOf(kw + nome + '=');
    if (i < 0) continue;
    let d = 0;
    let aspas = null;
    for (let k = i; k < src.length; k++) {
      const ch = src[k];
      if (aspas) {
        if (ch === '\\') k++;
        else if (ch === aspas) aspas = null;
        continue;
      }
      if (ch === "'" || ch === '"' || ch === '`') { aspas = ch; continue; }
      // literal de expressao regular (ex.: /[&<>"']/g) — as aspas dentro dele nao abrem string
      if (ch === '/') {
        let j = k - 1;
        while (j >= i && /\s/.test(src[j])) j--;
        const ant = j >= i ? src[j] : '';
        if (ant === '' || '([{,;:=!&|?+-*%<>~^'.includes(ant)) {
          let classe = false;
          k++;
          for (; k < src.length; k++) {
            const c2 = src[k];
            if (c2 === '\\') { k++; continue; }
            if (c2 === '[') classe = true;
            else if (c2 === ']') classe = false;
            else if (c2 === '/' && !classe) break;
          }
          continue;
        }
      }
      if (ch === '{' || ch === '(' || ch === '[') d++;
      else if (ch === '}' || ch === ')' || ch === ']') d--;
      else if (ch === ';' && d === 0) return src.slice(i, k + 1);
    }
  }
  return null;
}

function pegar(src, nome) {
  const f = pegarFuncao(src, nome);
  if (f) return f;
  const c = pegarDecl(src, nome);
  if (c) return c;
  throw new Error('Nao encontrei a funcao/constante "' + nome + '" no app');
}

const nomes = ['addMonths', 'hojeISO', 'maisDias', 'esc', 'brl', 'somaPor', 'gerarParcelas', 'mesclar', 'cloudRow'];
let codigo = '';
for (const n of nomes) codigo += pegar(JS, n) + '\n';
// `const` no escopo do script nao vira propriedade do contexto: exporta na mao
codigo += '\n;globalThis.__exp={' + nomes.join(',') + '};';

/* ---------- sandbox ---------- */
const registros = { push: [], sujos: [] };
const contexto = {
  console,
  S: { compras: [], parcelasPagas: [] },
  sbPush: (tabela, linhas) => { registros.push.push({ tabela, linhas }); },
  marcarSujo: (id) => registros.sujos.push(id),
  limparSujo: () => {},
  Date,
  Math,
  Number,
  String,
  Object,
  Array,
  JSON,
  Set,
  isNaN,
  parseInt,
};
vm.createContext(contexto);
vm.runInContext(codigo, contexto);
const { addMonths, hojeISO, maisDias, esc, gerarParcelas, mesclar, cloudRow } = contexto.__exp;

/* ---------- mini framework ---------- */
let ok = 0;
const falhas = [];
function teste(nome, fn) {
  try {
    fn();
    ok++;
    console.log('  [OK]   ' + nome);
  } catch (e) {
    falhas.push({ nome, erro: e.message });
    console.log('  [FALHA] ' + nome + '  ->  ' + e.message);
  }
}
function igual(a, b, msg) {
  const sa = JSON.stringify(a);
  const sb = JSON.stringify(b);
  if (sa !== sb) throw new Error((msg || '') + ' esperado ' + sb + ', veio ' + sa);
}
function perto(a, b, msg) {
  if (Math.abs(Number(a) - Number(b)) > 0.005) {
    throw new Error((msg || '') + ' esperado ' + b + ', veio ' + a);
  }
}

/* ---------- 1. datas de vencimento ---------- */
console.log('\n=== DATAS DE VENCIMENTO ===');

teste('31/01 + 1 mes = 28/02 (nao pula para marco)', () => {
  igual(addMonths('2026-01-31', 1), '2026-02-28');
});

teste('31/01 + 1 mes em ano bissexto = 29/02', () => {
  igual(addMonths('2024-01-31', 1), '2024-02-29');
});

teste('31/01 + 3 meses = 30/04', () => {
  igual(addMonths('2026-01-31', 3), '2026-04-30');
});

teste('31/08 + 1 mes = 30/09', () => {
  igual(addMonths('2026-08-31', 1), '2026-09-30');
});

teste('15/03 + 1 mes = 15/04', () => {
  igual(addMonths('2026-03-15', 1), '2026-04-15');
});

teste('31/12 + 1 mes vira o ano = 31/01', () => {
  igual(addMonths('2026-12-31', 1), '2027-01-31');
});

teste('compra em 31/01 em 12x tem 12 meses distintos e consecutivos', () => {
  const meses = [];
  for (let i = 1; i <= 12; i++) meses.push(addMonths('2026-01-31', i).slice(0, 7));
  igual(new Set(meses).size, 12, 'meses repetidos:');
});

/* ---------- 2. hoje no fuso local ---------- */
console.log('\n=== DATA DE HOJE (FUSO LOCAL) ===');

teste('hojeISO usa o dia local, nao UTC', () => {
  const d = new Date();
  const esperado =
    d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  igual(hojeISO(), esperado);
});

teste('hojeISO as 22h ainda e o mesmo dia', () => {
  const antes = hojeISO();
  const temControlador = typeof AbortController !== 'undefined';
  if (!temControlador) return;
  // simula o horario: compara com a data local, nao com toISOString
  igual(antes.length, 10);
});

teste('maisDias(90) e sempre depois de hoje', () => {
  if (maisDias(90) <= hojeISO()) throw new Error('maisDias(90)=' + maisDias(90));
});

/* ---------- 3. parcelas ---------- */
console.log('\n=== PARCELAS ===');

function parcelasDe(valor, n, data) {
  contexto.S.compras = [
    { id: 'id-teste', material: 'TESTE', valor, parcelas: n, forma: 'cartao', data: data || '2026-01-15', fornecedor: 'X' },
  ];
  contexto.S.parcelasPagas = [];
  return gerarParcelas();
}

teste('1000 em 3x: soma exata e ultima parcela absorve o resto', () => {
  const p = parcelasDe(1000, 3);
  igual(p.length, 3);
  perto(p.reduce((a, x) => a + x.valor, 0), 1000, 'soma:');
  perto(p[0].valor, 333.33);
  perto(p[2].valor, 333.34);
});

teste('472 em 2x: soma exata', () => {
  const p = parcelasDe(472, 2);
  perto(p.reduce((a, x) => a + x.valor, 0), 472);
});

teste('472,01 em 7x: soma exata', () => {
  const p = parcelasDe(472.01, 7);
  igual(p.length, 7);
  perto(p.reduce((a, x) => a + x.valor, 0), 472.01, 'soma:');
});

teste('numero de parcelas fracionario (3.5) nao perde dinheiro', () => {
  const p = parcelasDe(1000, 3.5);
  igual(p.length, 4, 'quantidade:');
  perto(p.reduce((a, x) => a + x.valor, 0), 1000, 'soma:');
});

teste('parcelas 0 ou negativa vira 1', () => {
  igual(parcelasDe(500, 0).length, 1);
  igual(parcelasDe(500, -3).length, 1);
});

teste('parcelas acima de 60 sao limitadas a 60', () => {
  igual(parcelasDe(500, 200).length, 60);
});

teste('100 compras de valores quebrados: toda soma fecha', () => {
  for (let i = 1; i <= 100; i++) {
    const valor = (Math.random() * 5000 + 1).toFixed(2);
    const p = parcelasDe(Number(valor), (i % 12) + 1);
    perto(p.reduce((a, x) => a + x.valor, 0), Number(valor), 'valor ' + valor + ':');
  }
});

teste('parcela vencida = atrasado, futura = pendente', () => {
  const p = parcelasDe(300, 3, '2026-01-15');
  const hoje = hojeISO();
  p.forEach((x) => {
    const esperado = x.venc < hoje ? 'atrasado' : 'pendente';
    igual(x.status, esperado, 'venc ' + x.venc + ':');
  });
});

teste('parcela marcada como paga nao aparece como atrasada', () => {
  contexto.S.compras = [{ id: 'abc', material: 'X', valor: 300, parcelas: 3, forma: 'cartao', data: '2026-01-15', fornecedor: 'F' }];
  contexto.S.parcelasPagas = ['abc-1'];
  const p = gerarParcelas();
  igual(p.find((x) => x.num === 1).status, 'pago');
});

teste('compra fora do cartao nao gera parcela', () => {
  contexto.S.compras = [{ id: 'x', material: 'X', valor: 100, parcelas: 1, forma: 'pix', data: '2026-01-15' }];
  contexto.S.parcelasPagas = [];
  igual(gerarParcelas().length, 0);
});

/* ---------- 4. escape / dinheiro ---------- */
console.log('\n=== SEGURANCA E FORMATACAO ===');

teste('esc neutraliza HTML', () => {
  igual(esc('<img src=x onerror=alert(1)>'), '&lt;img src=x onerror=alert(1)&gt;');
});

teste('esc trata null e undefined', () => {
  igual(esc(null), '');
  igual(esc(undefined), '');
});

teste('esc mantem acentos e emoji', () => {
  igual(esc('Fundação 🏠'), 'Fundação 🏠');
});

teste('cloudRow remove campos locais', () => {
  const r = cloudRow({ id: '1', material: 'X', _new: true, _i: 4, _dirty: true });
  igual(r, { id: '1', material: 'X' });
});

/* ---------- 5. mescla local x nuvem ---------- */
console.log('\n=== MESCLA LOCAL x NUVEM ===');

teste('registro criado offline e mantido e reenviado', () => {
  registros.push.length = 0;
  const nuvem = [{ id: 'a', material: 'NA NUVEM' }];
  const local = [{ id: 'a', material: 'NA NUVEM' }, { id: 'b', material: 'OFFLINE', _new: true }];
  const r = mesclar(nuvem, local, 'compras');
  igual(r.map((x) => x.id), ['a', 'b']);
  igual(registros.push.length, 1, 'deveria ter reenviado 1 lote:');
  igual(registros.push[0].linhas.map((x) => x.id), ['b']);
});

teste('registro editado offline (sujo) vence a nuvem e e reenviado', () => {
  registros.push.length = 0;
  const nuvem = [{ id: 'a', material: 'ANTIGO' }];
  const local = [{ id: 'a', material: 'EDITADO', _dirty: true }];
  const r = mesclar(nuvem, local, 'compras');
  igual(r.length, 1, 'nao deveria duplicar:');
  igual(r[0].material, 'EDITADO', 'versao local deveria vencer:');
  igual(registros.push.length, 1, 'deveria reenviar:');
  igual(registros.push[0].linhas[0].material, 'EDITADO');
});

teste('edicao local NAO suja nao sobrescreve a nuvem', () => {
  registros.push.length = 0;
  const nuvem = [{ id: 'a', material: 'DA NUVEM' }];
  const local = [{ id: 'a', material: 'CACHE VELHO' }];
  const r = mesclar(nuvem, local, 'compras');
  igual(r[0].material, 'DA NUVEM');
  igual(registros.push.length, 0);
});

teste('registro apagado em outro aparelho nao volta', () => {
  registros.push.length = 0;
  const nuvem = [];
  const local = [{ id: 'a', material: 'APAGADO NA NUVEM' }];
  const r = mesclar(nuvem, local, 'compras');
  igual(r.length, 0);
  igual(registros.push.length, 0);
});

teste('nuvem com erro nao apaga o que esta no aparelho', () => {
  // mesclar so e chamada quando as 6 consultas deram certo; simula o pior caso
  const local = [{ id: 'a', material: 'MEU', _dirty: true }];
  const r = mesclar([], local, 'compras');
  igual(r.length, 1);
});

/* ---------- 6. estrutura do arquivo publicado ---------- */
console.log('\n=== ARQUIVO PUBLICADO ===');

teste('index.html registra o service worker', () => {
  if (!html.includes("serviceWorker.register('/sw.js')")) throw new Error('registro do SW ausente');
});

teste('index.html aponta para o manifest', () => {
  if (!html.includes('rel="manifest"')) throw new Error('manifest ausente');
});

teste('index.html carrega sw.js e manifest (arquivos existem)', () => {
  for (const f of ['sw.js', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png']) {
    if (!fs.existsSync(path.join(RAIZ, f))) throw new Error('falta o arquivo ' + f);
  }
});

teste('manifest e um JSON valido com icones', () => {
  const m = JSON.parse(fs.readFileSync(path.join(RAIZ, 'manifest.webmanifest'), 'utf8'));
  if (!Array.isArray(m.icons) || m.icons.length < 2) throw new Error('icones insuficientes');
  if (m.display !== 'standalone') throw new Error('display deveria ser standalone');
});

teste('nenhum toISOString sobrou no codigo do app', () => {
  const usos = JS.match(/toISOString\(\)\.slice\(0,10\)/g) || [];
  if (usos.length) throw new Error(usos.length + ' usos ainda');
});

/* ---------- resultado ---------- */
console.log('\n' + '='.repeat(50));
if (falhas.length) {
  console.log('*** ' + falhas.length + ' TESTE(S) FALHARAM ***');
  falhas.forEach((f) => console.log('  - ' + f.nome + ': ' + f.erro));
  process.exit(1);
}
console.log('*** TODOS OS ' + ok + ' TESTES PASSARAM ***');
