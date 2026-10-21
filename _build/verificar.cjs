// Verificacao do app - SEM "new Function" (evita a heuristica de script do Kaspersky)
// Checagem de sintaxe feita com "node --check" em arquivo .js solido.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const APP = 'C:/Users/Odair/Documents/App Caio/index.html';
const html = fs.readFileSync(APP, 'utf-8');

const m = html.match(/const SEED=(\{[\s\S]*?});/);
if (!m) { console.error('SEED nao encontrado'); process.exit(1); }
const S = JSON.parse(m[1]);

const brl = n => 'R$ ' + Number(n).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
let falhas = 0;
const ok = (cond, msg) => { console.log((cond ? '  [OK]   ' : '  [FALHA] ') + msg); if (!cond) falhas++; };

console.log('=== CONTAGENS ===');
ok(S.compras.length === 243, 'compras = ' + S.compras.length + ' (esperado 243)');
ok(S.maoDeObra.length === 32, 'maoDeObra = ' + S.maoDeObra.length + ' (esperado 32)');
ok(S.documentos.length === 30, 'documentos = ' + S.documentos.length + ' (esperado 30)');
ok(S.juros.length === 14, 'juros = ' + S.juros.length + ' (esperado 14)');
ok(S.contas.length === 13, 'contas = ' + S.contas.length + ' (esperado 13)');
ok(S.rateio.length === 7, 'rateio = ' + S.rateio.length + ' (esperado 7)');

console.log('\n=== MAO DE OBRA ===');
const somaMO = S.maoDeObra.reduce((a, b) => a + Number(b.valor || 0), 0);
ok(Math.abs(somaMO - 62007.32) < 0.01, 'soma = ' + brl(somaMO) + ' (esperado R$ 62.007,32)');
ok(S.maoDeObra.every(r => r.data && !/total|saldo/i.test(r.data || '')), 'nenhuma linha TOTAL/SALDO');
ok(S.maoDeObra.every(r => Number(r.valor) >= 0), 'nenhum valor negativo');

console.log('\n=== IDS EM UUID ===');
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
[['compras', S.compras], ['maoDeObra', S.maoDeObra], ['documentos', S.documentos],
 ['juros', S.juros], ['contas', S.contas]].forEach(([nome, arr]) => {
  const bons = arr.filter(r => r.id && UUID.test(r.id)).length;
  ok(bons === arr.length, nome + ': ' + bons + '/' + arr.length + ' ids em UUID');
});
const todos = [...S.compras, ...S.maoDeObra, ...S.documentos, ...S.juros, ...S.contas].map(r => r.id);
ok(new Set(todos).size === todos.length, 'ids unicos (' + todos.length + ' registros)');

console.log('\n=== DIVISAO / RESUMO DA OBRA ===');
const R = S.resumoDivisao || {};
ok(Math.abs((R['VALOR DEVIDO'] || 0) - 31420.34) < 0.05, 'VALOR DEVIDO = ' + brl(R['VALOR DEVIDO']) + ' (esperado R$ 31.420,34)');
ok((R['VALOR TERRENO'] || 0) === 35000, 'VALOR TERRENO = ' + brl(R['VALOR TERRENO']));
ok(!!S.obra && S.obra.area === 72, 'obra: ' + S.obra.area + ' m2 a ' + brl(S.obra.valorM2) + '/m2');

console.log('\n=== SINTAXE DO JS DO APP (node --check) ===');
const scripts = [...html.matchAll(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g)].map(x => x[1]);
console.log('  blocos <script> encontrados: ' + scripts.length);
const tmp = path.join(os.tmpdir(), 'app_check_' + process.pid + '.js');
try {
  scripts.forEach((code, i) => {
    fs.writeFileSync(tmp, code, 'utf-8');
    try {
      execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' });
      console.log('  [OK]   bloco ' + i + ' (' + code.length + ' chars) - sintaxe valida');
    } catch (e) {
      console.log('  [FALHA] bloco ' + i + ': ' + String(e.stderr || e.message).slice(0, 400));
      falhas++;
    }
  });
} finally { try { fs.unlinkSync(tmp); } catch (e) {} }

console.log('\n=== SUPABASE ===');
const url = (html.match(/SUPABASE_URL\s*=\s*'([^']+)'/) || [])[1] || '';
ok(url === 'https://nvzqjvltzhmbtbtwletv.supabase.co', 'URL: ' + url);
ok(html.includes('crypto.randomUUID'), 'uid() gera UUID');

console.log('\n' + (falhas === 0 ? '*** TUDO OK ***' : '*** ' + falhas + ' FALHA(S) ***'));
process.exit(falhas === 0 ? 0 : 1);
