import json
import datetime
import uuid

_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
def _uid(chave):
    """Gera UUID determinístico (mesmo registro = mesmo id sempre)."""
    return str(uuid.uuid5(_NS, "obra-caio:" + str(chave)))

def _is_real_date(s):
    """Valida se é uma data ISO verdadeira."""
    if not s:
        return False
    try:
        datetime.date.fromisoformat(str(s).strip())
        return True
    except Exception:
        return False

def _is_summary(v):
    """True quando a célula é um rótulo de resumo (ex: TOTAL, SALDO) e não uma data."""
    if v is None or str(v).strip() == "":
        return False
    return not _is_real_date(v)

with open(r"C:\Users\Odair\Documents\App Caio\obra_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert spreadsheet data to Lovable-like structure
compras = []
for i, c in enumerate(data.get("custos", [])):
    if _is_summary(c.get("data")):
        continue  # pula linhas de resumo/total
    pag = (c.get("pagamento") or "").upper()
    forma = "cartao" if "CART" in pag else "pix" if "PIX" in pag else "dinheiro" if "DINHEIRO" in pag else "boleto" if "BOLETO" in pag else "outro"
    parcelas = 1
    if "CART" in pag:
        import re
        m = re.search(r'(\d+)\s*[xX]', pag)
        if m: parcelas = int(m.group(1))
    compras.append({
        "id": _uid("compra:" + str(i)), "quantidade": str(c.get("qtd") or ""), "material": c.get("material") or "",
        "valor": c.get("preco") or 0, "forma": forma, "parcelas": parcelas,
        "fornecedor": c.get("local"), "data": c.get("data"), "pagador": c.get("realizou"),
        "status": (c.get("status") or "PAGO").lower(), "categoria": "Outros"
    })

maoDeObra = []
for i, c in enumerate(data.get("mao_obra", [])):
    if _is_summary(c.get("data")):
        continue  # pula linhas TOTAL/SALDO da planilha
    maoDeObra.append({"id": _uid("mo:" + str(i)), "data": c.get("data") or "", "valor": c.get("valor") or 0,
        "descricao": c.get("quem") or c.get("forma") or "", "status": (c.get("status") or "PAGO").lower()})

documentos = []
for i, c in enumerate(data.get("documentacao", [])):
    if _is_summary(c.get("data")):
        continue
    documentos.append({"id": _uid("doc:" + str(i)), "servico": c.get("servico") or "", "valor": c.get("valor") or 0,
        "data": c.get("data"), "forma": c.get("pagamento"), "obs": c.get("obs")})

juros = []
for i, r in enumerate(data.get("juros", [])):
    if _is_summary(r.get("data")):
        continue
    juros.append({"id": _uid("juros:" + str(i)), "data": r.get("data"), "valor": r.get("valor")})

rateio = [r for r in data.get("divisao", []) if not _is_summary(r.get("data"))]
contas = []
for i, r in enumerate(data.get("utilidades", [])):
    contas.append({"id": _uid("contas:" + str(i)), "item": r.get("item"), "mes": r.get("mes"),
        "valor": r.get("valor"), "status": r.get("status")})

seed = {"compras": compras, "maoDeObra": maoDeObra, "documentos": documentos,
    "parcelasPagas": [], "juros": juros, "contas": contas,
    "rateio": rateio, "resumoDivisao": data.get("resumo_divisao", {}),
    "obra": {"area": 72, "valorM2": 1800}}

data_js = json.dumps(seed, ensure_ascii=False)

html = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Obra Fácil — Casa Caio</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
--bg:#09090b;--card:#111114;--card2:#18181b;--card3:#1f1f24;
--accent:#8b5cf6;--accent2:#a78bfa;--accent3:#c4b5fd;
--green:#10b981;--red:#ef4444;--orange:#f59e0b;--blue:#3b82f6;--pink:#ec4899;--teal:#14b8a6;
--text:#fafafa;--text2:#a1a1aa;--border:#27272a;
--chart1:#8b5cf6;--chart2:#10b981;--chart3:#3b82f6;--chart4:#f59e0b;--chart5:#ef4444;
--glow:0 0 30px rgba(139,92,246,.2);
--radius:12px;
}
html{font-family:'Inter',system-ui,sans-serif}
html,body{overflow-x:hidden;overflow-x:clip;max-width:100%}
body{background:var(--bg);color:var(--text);min-height:100vh}
.sidebar{position:fixed;left:0;top:0;bottom:0;width:240px;background:var(--card);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:24px 12px;gap:4px;z-index:100}
.sidebar .brand{display:flex;align-items:center;gap:10px;padding:0 8px 24px;border-bottom:1px solid var(--border);margin-bottom:16px}
.sidebar .brand .icon{font-size:32px}
.hamburger{display:none;background:none;border:none;color:var(--text);font-size:24px;cursor:pointer;padding:4px 8px}
.dots-menu{display:none;background:var(--card3);border:1px solid var(--border);color:var(--text);font-size:22px;cursor:pointer;padding:0 12px;height:40px;border-radius:10px;line-height:1;font-weight:700}
.nav-menu{display:flex;flex-direction:column;gap:4px}
.sidebar .brand h2{font-size:16px;font-weight:700}
.sidebar .brand p{font-size:11px;color:var(--text2)}
.sidebar .section{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:var(--text2);padding:16px 12px 6px}
.nav-btn{width:100%;height:44px;border-radius:var(--radius);border:none;background:transparent;color:var(--text2);font-size:14px;font-weight:500;cursor:pointer;display:flex;align-items:center;gap:12px;padding:0 14px;transition:all .2s}
.nav-btn:hover{background:var(--card3);color:var(--text)}
.nav-btn.active{background:var(--accent);color:#fff;box-shadow:var(--glow)}
.nav-btn .ico{font-size:18px;width:24px;text-align:center}
.main{margin-left:240px;padding:0 0 40px;min-width:0}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:20px 32px;border-bottom:1px solid var(--border);background:var(--card);position:sticky;top:0;z-index:50;backdrop-filter:blur(12px)}
.topbar h1{font-size:20px;font-weight:700}
.topbar .actions{display:flex;gap:10px;align-items:center}
.btn{padding:8px 18px;border-radius:var(--radius);border:none;cursor:pointer;font-size:13px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:var(--accent);color:#fff}.btn-primary:hover{background:var(--accent2);box-shadow:var(--glow)}
.btn-secondary{background:var(--card3);color:var(--text);border:1px solid var(--border)}.btn-secondary:hover{border-color:var(--accent)}
.btn-ghost{background:transparent;color:var(--text2)}.btn-ghost:hover{background:var(--card3);color:var(--text)}
.btn-danger{background:rgba(239,68,68,.1);color:var(--red)}.btn-danger:hover{background:var(--red);color:#fff}
.btn-icon{width:36px;height:36px;padding:0;justify-content:center;border-radius:8px}
.content{padding:24px 32px;overflow-x:hidden}
.page{display:none}.page.active{display:block}
/* HERO */
.hero{background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(16,185,129,.08));border:1px solid var(--border);border-radius:16px;padding:32px;margin-bottom:24px}
.hero .label{font-size:11px;text-transform:uppercase;letter-spacing:2px;color:var(--text2);margin-bottom:8px}
.hero .total{font-size:48px;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--teal));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero .sub{font-size:14px;color:var(--text2);margin-top:8px}
/* STATS */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.stats>*{min-width:0}
.stat{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;transition:all .3s}
.stat:hover{border-color:var(--accent);box-shadow:var(--glow)}
.stat .label{font-size:12px;color:var(--text2);margin-bottom:6px}
.stat .value{font-size:24px;font-weight:700}
.stat .hint{font-size:11px;color:var(--text2);margin-top:4px}
.stat.danger .value{color:var(--red)}.stat.primary .value{color:var(--accent2)}
/* CHARTS */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;min-width:0}
.grid2>*{min-width:0}
.grid3{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:24px;min-width:0}
.grid3>*{min-width:0}
@media(max-width:900px){.grid2,.grid3{grid-template-columns:1fr}}
.chart-box{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;height:350px;display:flex;flex-direction:column;min-width:0;overflow:hidden}
.chart-box h3{font-size:14px;font-weight:600;margin-bottom:16px;color:var(--accent2)}
.chart-box canvas{flex:1;min-height:0;max-width:100%}
/* TABLE */
.table-box{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;margin-bottom:24px;min-width:0;max-width:100%}
.table-box .header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid var(--border);flex-wrap:wrap;gap:12px}
.table-box .header h3{font-size:16px;font-weight:600;display:flex;align-items:center;gap:8px}
.table-box .header .count{background:var(--accent);color:#fff;font-size:11px;padding:3px 10px;border-radius:20px;font-weight:600}
.table-box .body{padding:0}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:12px 20px;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--text2);border-bottom:1px solid var(--border);background:var(--card2);cursor:pointer;user-select:none;position:sticky;top:0;z-index:1}
th:hover{color:var(--accent2)}
td{padding:14px 20px;border-bottom:1px solid rgba(39,39,42,.5);font-size:14px;vertical-align:middle}
tr:hover{background:rgba(139,92,246,.03)}
.table-wrap{max-height:550px;overflow-y:auto}
.parcela-list{max-height:550px;overflow-y:auto;padding:8px 20px}
.parcela-list::-webkit-scrollbar{width:5px}
.parcela-list::-webkit-scrollbar-thumb{background:var(--accent);border-radius:3px}
.mobile-list{display:none}
.table-wrap::-webkit-scrollbar{width:5px}
.table-wrap::-webkit-scrollbar-thumb{background:var(--accent);border-radius:3px}
/* BADGE */
.badge{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;text-transform:capitalize}
.badge.pago{background:rgba(16,185,129,.12);color:var(--green)}
.badge.pendente{background:rgba(245,158,11,.12);color:var(--orange)}
.badge.atrasado{background:rgba(239,68,68,.12);color:var(--red)}
.badge.cat{background:var(--card3);color:var(--text2);font-size:10px}
.new-badge{display:inline-block;background:var(--green);color:#fff;font-size:9px;padding:1px 6px;border-radius:8px;margin-left:4px;vertical-align:middle;font-weight:700}
/* FILTERS */
.filters{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;align-items:center}
.filters input,.filters select{background:var(--card2);border:1px solid var(--border);border-radius:8px;padding:9px 14px;color:var(--text);font-size:13px;outline:none;transition:border .2s;font-family:inherit}
.filters input:focus,.filters select:focus{border-color:var(--accent)}
.filters input{min-width:220px}
/* MODAL */
.modal-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.6);z-index:200;justify-content:center;align-items:center;backdrop-filter:blur(8px)}
.modal-overlay.open{display:flex}
.modal{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:32px;width:520px;max-width:95vw;max-height:90vh;overflow-y:auto;box-shadow:0 25px 60px rgba(0,0,0,.5)}
.modal h2{font-size:20px;margin-bottom:24px;color:var(--accent2);display:flex;align-items:center;gap:10px}
.form-group{margin-bottom:14px}
.form-group label{display:block;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--text2);margin-bottom:5px;font-weight:600}
.form-group input,.form-group select{width:100%;background:var(--card2);border:1px solid var(--border);border-radius:8px;padding:11px 14px;color:var(--text);font-size:14px;outline:none;transition:border .2s;font-family:inherit}
.form-group input:focus,.form-group select:focus{border-color:var(--accent)}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.btn-group{display:flex;gap:10px;margin-top:24px;justify-content:flex-end}
/* TOAST */
.toast{position:fixed;bottom:24px;right:24px;background:var(--green);color:#fff;padding:14px 24px;border-radius:var(--radius);font-weight:600;font-size:14px;z-index:300;transform:translateY(100px);opacity:0;transition:all .4s;display:flex;align-items:center;gap:10px}
.toast.show{transform:translateY(0);opacity:1}
.toast.error{background:var(--red)}
.toast .undo{background:rgba(255,255,255,.2);border:none;color:#fff;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600}
/* SPLIT */
.split-box{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:28px}
.split-box h3{color:var(--accent2);margin-bottom:20px;font-size:16px}
.split-item{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border)}
.split-item:last-child{border:none;font-size:17px;font-weight:700;color:var(--accent2)}
/* PARCELAS */
.parcela-row{display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--border)}
.parcela-row:last-child{border:none}
.parcela-check{width:32px;height:32px;border-radius:8px;border:2px solid var(--border);background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;color:transparent}
.parcela-check.paid{background:var(--green);border-color:var(--green);color:#fff}
.parc-sub{color:var(--text2);font-size:13px;margin:-10px 0 22px}
.parc-grid{display:grid;grid-template-columns:1fr 1.7fr;gap:20px;margin-bottom:24px;min-width:0}
@media(max-width:900px){.parc-grid{grid-template-columns:1fr;gap:12px}}
.pmes-list{padding:8px 20px 16px}
.pmes-row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid rgba(39,39,42,.5);font-size:13.5px;color:var(--text2)}
.pmes-row:last-child{border-bottom:none}
.pmes-row b{color:var(--text);font-weight:600;white-space:nowrap}
.parc-items{max-height:600px;overflow-y:auto;padding:6px 20px 16px}
.parc-items::-webkit-scrollbar{width:5px}
.parc-items::-webkit-scrollbar-thumb{background:var(--accent);border-radius:3px}
.parc-item{display:flex;align-items:center;gap:14px;padding:13px 0;border-bottom:1px solid rgba(39,39,42,.5)}
.parc-item:last-child{border-bottom:none}
.pi-main{flex:1;min-width:0}
.pi-title{font-size:13.5px;font-weight:600;text-transform:uppercase;letter-spacing:.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pi-sub{font-size:11.5px;color:var(--text2);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pi-valor{font-size:14.5px;font-weight:700;white-space:nowrap}
.btn-pago{display:inline-flex;align-items:center;gap:5px;background:var(--card2);border:1px solid var(--border);color:var(--text);padding:6px 13px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .2s;white-space:nowrap}
.btn-pago:hover{background:var(--green);border-color:var(--green);color:#fff}
@media(max-width:768px){.parc-item{flex-wrap:wrap;gap:10px}.pi-main{flex:1 1 100%}.pi-valor{margin-left:auto}.parc-items{max-height:none;overflow:visible}.pmes-list,.parc-items{padding-left:16px;padding-right:16px}}
/* JUROS & ACERTO */
.jc-box{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;margin-bottom:24px;min-width:0;display:flex;flex-direction:column}
.jc-box h3{font-size:16px;font-weight:600;margin-bottom:20px}
.jc-chart{position:relative;height:230px}
.jc-chart canvas{position:absolute;inset:0;width:100%!important;height:100%!important}
.jc-cap{font-size:12px;color:var(--text2);margin-top:16px}
.jc-list{flex:1}
.jc-item{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:12px 0;border-bottom:1px solid rgba(39,39,42,.5);font-size:13.5px;color:var(--text2)}
.jc-item .jc-val{color:var(--text);font-weight:600;white-space:nowrap}
.jc-item.neg .jc-val{color:var(--text2);font-weight:500}
.jc-total{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:14px 0 2px;font-size:15px;font-weight:700;color:var(--text)}
.jc-total .jc-val{color:var(--accent2);font-size:16.5px;white-space:nowrap}
.jc-row{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:12px 0;border-bottom:1px solid rgba(39,39,42,.5);font-size:13.5px}
.jc-row:last-of-type{border-bottom:none}
.jc-name{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.jc-date{font-size:11.5px;color:var(--text2);margin-left:8px;white-space:nowrap}
.jc-valor{font-weight:600;white-space:nowrap}
.jc-totrow{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:14px 0 2px;margin-top:4px;border-top:1px solid var(--border);font-size:15px;font-weight:700}
@media(max-width:768px){.jc-item,.jc-row,.jc-total,.jc-totrow{gap:10px}.jc-name{white-space:normal}.jc-chart{height:200px}}
@media(max-width:768px){
.sidebar{width:100%;height:auto;bottom:auto;flex-direction:column;padding:0;align-items:stretch;border-right:none;border-bottom:1px solid var(--border);position:fixed;top:0}
.sidebar .brand{border:none;margin:0;padding:12px 16px;justify-content:space-between}
.sidebar .brand p{display:none}
.sidebar .brand h2{display:block;font-size:18px}
.hamburger{display:block;background:none;border:none;color:var(--text);font-size:24px;cursor:pointer;padding:4px 8px}
.nav-menu{display:none;flex-direction:column;padding:8px;gap:2px}
.nav-menu.open{display:flex}
.sidebar .section{display:none}
.nav-btn{width:100%;height:48px;padding:0 16px;font-size:14px;border-radius:10px}
.nav-btn .ico{font-size:20px;width:28px}
.main{margin-left:0;margin-top:64px;width:auto;max-width:none}.content{padding:12px}.topbar{padding:12px;top:64px}
.dots-menu{display:block}
.topbar h1{font-size:16px}
.stats{grid-template-columns:1fr 1fr;gap:10px}
.hero{padding:20px}.hero .total{font-size:28px}.hero .sub{font-size:12px}
.stat{padding:14px}.stat .value{font-size:18px}
.form-row{grid-template-columns:1fr}
.grid2,.grid3{grid-template-columns:1fr;gap:12px}
.chart-box{height:280px;padding:16px}
.chart-box h3{font-size:13px}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;display:none}
.mobile-list{display:block}
.mcard{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid rgba(39,39,42,.6)}
.mcard:last-child{border-bottom:none}
.mcard .mi{flex:1;min-width:0}
.mcard .mt{font-size:14px;font-weight:600;line-height:1.3;word-break:break-word}
.mcard .ms{font-size:11.5px;color:var(--text2);margin-top:4px;line-height:1.4}
.mcard .mr{text-align:right;flex-shrink:0;display:flex;flex-direction:column;align-items:flex-end;gap:6px}
.mcard .mv{font-size:15px;font-weight:700;color:var(--accent2)}
.mcard .ma{display:flex;gap:6px}
table{min-width:600px}
th,td{padding:10px 12px;font-size:12px}
.filters{flex-direction:column;align-items:stretch}
.filters input,.filters select{min-width:auto;width:100%}
.filters .btn{width:100%;justify-content:center;height:44px}
.modal{width:100%;max-height:85vh;border-radius:16px 16px 0 0;padding:20px;position:fixed;bottom:0;left:0;right:0;max-width:100%}
.modal-overlay{align-items:flex-end}
.modal h2{font-size:16px;margin-bottom:16px}
.btn{height:44px;font-size:14px}
.btn-group{flex-direction:column}.btn-group .btn{width:100%;justify-content:center}
.toast{left:12px;right:12px;bottom:12px;justify-content:center}
.parcela-row{flex-wrap:wrap}
.split-box{padding:16px}
.split-item{font-size:13px}
}
@media(max-width:480px){
.stats{grid-template-columns:1fr}
.hero .total{font-size:24px}
}
</style>
</head>
<body>
<div class="sidebar">
<div class="brand"><span class="icon">🏠</span><h2>Obra Fácil</h2></div>
<div class="nav-menu">
<div class="section">Menu</div>
<button class="nav-btn active" onclick="show('dashboard',this);closeMenu()"><span class="ico">📊</span>Painel</button>
<button class="nav-btn" onclick="show('compras',this);closeMenu()"><span class="ico">🧱</span>Compras</button>
<button class="nav-btn" onclick="show('parcelas',this);closeMenu()"><span class="ico">💳</span>Parcelas</button>
<button class="nav-btn" onclick="show('maoobra',this);closeMenu()"><span class="ico">👷</span>Mão de Obra</button>
<button class="nav-btn" onclick="show('documentos',this);closeMenu()"><span class="ico">📋</span>Documentos</button>
<div class="section">Financeiro</div>
<button class="nav-btn" onclick="show('financiamento',this);closeMenu()"><span class="ico">🏦</span>Financiamento</button>
<button class="nav-btn" onclick="show('juros',this);closeMenu()"><span class="ico">📈</span>Juros & acerto</button>
<button class="nav-btn" onclick="show('divisao',this);closeMenu()"><span class="ico">🤝</span>Rateio Matheus</button>
</div>
</div>

<div class="main">
<div class="topbar">
<button class="dots-menu" onclick="toggleNav()" title="Menu">☰</button>
<h1 id="pageTitle">Painel</h1>
</div>

<div class="content">
<!-- DASHBOARD -->
<div id="page-dashboard" class="page active">
<div class="hero">
<div class="label">Total investido (sem terreno)</div>
<div class="total" id="heroTotal"></div>
<div class="sub" id="heroSub"></div>
</div>
<div class="stats" id="statsGrid"></div>
<div class="grid3">
<div class="chart-box"><h3>📊 Compras de material por mês</h3><canvas id="chartMes"></canvas></div>
<div class="chart-box"><h3>🍩 Para onde foi o dinheiro</h3><canvas id="chartCat"></canvas></div>
</div>
<div class="grid2">
<div class="chart-box"><h3>💳 Forma de pagamento</h3><canvas id="chartPag"></canvas></div>
<div class="chart-box"><h3>🏪 Fornecedores top 8</h3><canvas id="chartForn"></canvas></div>
</div>
</div>

<!-- COMPRAS -->
<div id="page-compras" class="page">
<div class="filters">
<input type="text" id="cq" placeholder="🔍 Buscar material..." oninput="renderCompras()">
<select id="cforn" onchange="renderCompras()"><option value="">Todos fornecedores</option></select>
<select id="ccat" onchange="renderCompras()"><option value="">Todas etapas</option></select>
<select id="cforma" onchange="renderCompras()"><option value="">Todas formas</option></select>
<button class="btn btn-primary" onclick="openModal('compra')">➕ Nova compra</button>
</div>
<div class="table-box"><div class="table-wrap"><table>
<thead><tr><th onclick="sortC('data')">Data ↕</th><th onclick="sortC('material')">Material ↕</th><th onclick="sortC('valor')">Valor ↕</th><th>Fornecedor</th><th>Pagamento</th><th>Etapa</th><th>Status</th><th>Ações</th></tr></thead>
<tbody id="comprasBody"></tbody></table></div><div class="mobile-list" id="comprasCards"></div></div>
</div>

<!-- PARCELAS -->
<div id="page-parcelas" class="page">
<p class="parc-sub">💳 Cartão em N vezes vira N parcelas mensais automaticamente</p>
<div class="stats" id="parcelasStats"></div>
<div class="parc-grid">
<div class="table-box"><div class="header"><h3>📅 Por fatura (mês)</h3></div>
<div class="pmes-list" id="parcPorMes"></div></div>
<div class="table-box"><div class="header"><h3>💳 Parcelas em aberto</h3><span class="count" id="parcCount"></span></div>
<div class="parc-items" id="parcelasList"></div></div>
</div>
</div>

<!-- MÃO DE OBRA -->
<div id="page-maoobra" class="page">
<div class="filters">
<button class="btn btn-primary" onclick="openModal('maoobra')">➕ Novo pagamento</button>
</div>
<div class="stats" id="moStats"></div>
<div class="grid2">
<div class="chart-box"><h3>👷 Pagamentos por mês</h3><canvas id="chartMo"></canvas></div>
<div class="chart-box"><h3>📈 Evolução acumulada</h3><canvas id="chartMoAcum"></canvas></div>
</div>
<div class="table-box"><div class="table-wrap"><table>
<thead><tr><th>Data</th><th>Valor</th><th>Descrição</th><th>Status</th><th></th></tr></thead>
<tbody id="moBody"></tbody></table></div><div class="mobile-list" id="moCards"></div></div>
</div>

<!-- DOCUMENTOS -->
<div id="page-documentos" class="page">
<div class="filters">
<button class="btn btn-primary" onclick="openModal('doc')">➕ Novo serviço</button>
</div>
<div class="stats" id="docStats"></div>
<div class="grid2">
<div class="chart-box"><h3>📋 Custos por mês</h3><canvas id="chartDoc"></canvas></div>
<div class="chart-box"><h3>🥧 Top serviços</h3><canvas id="chartDocPie"></canvas></div>
</div>
<div class="table-box"><div class="table-wrap"><table>
<thead><tr><th>Serviço</th><th>Valor</th><th>Data</th><th>Pagamento</th><th></th></tr></thead>
<tbody id="docBody"></tbody></table></div><div class="mobile-list" id="docCards"></div></div>
</div>

<!-- FINANCIAMENTO -->
<div id="page-financiamento" class="page">
<div class="stats" id="finStats"></div>
<div class="grid2">
<div class="chart-box"><h3>🏦 Parcelas do financiamento</h3><canvas id="chartFin"></canvas></div>
<div class="chart-box"><h3>💡 Contas da obra</h3><canvas id="chartContas"></canvas></div>
</div>
<div class="table-box"><div class="header"><h3>🏦 Financiamento</h3></div><div class="table-wrap"><table>
<thead><tr><th>Vencimento</th><th>Valor</th><th></th></tr></thead>
<tbody id="finBody"></tbody></table></div><div class="mobile-list" id="finCards"></div></div>
<div class="table-box"><div class="header"><h3>💡 Contas (Água/Luz/IPTU)</h3></div><div class="table-wrap"><table>
<thead><tr><th>Item</th><th>Mês</th><th>Valor</th><th>Status</th><th></th></tr></thead>
<tbody id="contasBody"></tbody></table></div><div class="mobile-list" id="contasCards"></div></div>
</div>

<!-- JUROS & ACERTO -->
<div id="page-juros" class="page">
<p class="parc-sub">📈 Financiamento da obra e divisão com sócio</p>
<div class="stats" id="jStats"></div>
<div class="jc-box"><h3>📈 Curva dos juros de obra</h3>
<div class="jc-chart"><canvas id="chartJuros"></canvas></div>
<p class="jc-cap">Os juros sobem a cada liberação de etapa pelo banco.</p></div>
<div class="grid2">
<div class="jc-box"><h3>🤝 Acerto com Matheus</h3><div class="jc-list" id="acertoBox"></div></div>
<div class="jc-box"><h3>📄 Despesas divididas</h3><div class="jc-list" id="despBox"></div></div>
</div>
</div>

<!-- DIVISÃO -->
<div id="page-divisao" class="page">
<div class="grid2">
<div class="split-box" id="splitBox"></div>
<div class="chart-box"><h3>🤝 Composição do rateio</h3><canvas id="chartSplit"></canvas></div>
</div>
<div class="table-box"><div class="header"><h3>🤝 Detalhamento</h3></div><div class="table-wrap"><table>
<thead><tr><th>Item</th><th>Valor</th><th>Data</th></tr></thead>
<tbody id="splitBody"></tbody></table></div><div class="mobile-list" id="splitCards"></div></div>
</div>
</div>
</div>

<!-- MODAL -->
<div class="modal-overlay" id="modal">
<div class="modal">
<h2 id="modalTitle"></h2>
<div id="modalBody"></div>
<div class="btn-group">
<button class="btn btn-secondary" onclick="closeModal()">Cancelar</button>
<button class="btn btn-primary" onclick="saveEntry()">💾 Salvar</button>
</div>
</div>
</div>

<div class="toast" id="toast"></div>

<script>
const SEED=__DATA__;

// ============================================
// SUPABASE CONFIG — Cole sua URL e anon key aqui
// ============================================
const SUPABASE_URL='https://nvzqjvltzhmbtbtwletv.supabase.co';
const SUPABASE_KEY='sb_publishable_mLCxvus4BzQcvwc1lH2alQ_Ci9gI6Hw';
const SB=typeof supabase!=='undefined'&&SUPABASE_URL!=='SUA_URL_SUPABASE'?supabase.createClient(SUPABASE_URL,SUPABASE_KEY):null;
async function sbPush(table,payload){
if(!SB)return null;
try{const{data,error}=await SB.from(table).insert(payload);if(error)throw error;return data}catch(e){console.warn('Supabase push error:',e.message);return null}}
async function sbUpdate(table,id,payload){
if(!SB)return null;
try{const{data,error}=await SB.from(table).update(payload).eq('id',id);if(error)throw error;return data}catch(e){console.warn('Supabase update error:',e.message);return null}}
async function sbDelete(table,id){
if(!SB)return null;
try{const{error}=await SB.from(table).delete().eq('id',id);if(error)throw error;return true}catch(e){console.warn('Supabase delete error:',e.message);return null}}
async function sbPullAll(silent){
if(!SB)return;
try{
const[rc,rm,rd,rp,rj,rc2]=await Promise.all([
SB.from('compras').select('*'),SB.from('mao_de_obra').select('*'),SB.from('documentos').select('*'),
SB.from('parcelas_pagas').select('*'),SB.from('juros').select('*'),SB.from('contas').select('*')]);
if(rc.data&&rc.data.length)S.compras=rc.data.map(r=>({id:r.id,quantidade:r.quantidade,material:r.material,valor:Number(r.valor),forma:r.forma,parcelas:r.parcelas,fornecedor:r.fornecedor,data:r.data,pagador:r.pagador,status:r.status,categoria:r.categoria}));
if(rm.data&&rm.data.length)S.maoDeObra=rm.data.map(r=>({id:r.id,data:r.data,valor:Number(r.valor),descricao:r.descricao,status:r.status}));
if(rd.data&&rd.data.length)S.documentos=rd.data.map(r=>({id:r.id,servico:r.servico,valor:Number(r.valor),data:r.data,forma:r.forma,obs:r.obs}));
if(rp.data)S.parcelasPagas=rp.data.map(r=>r.parcela_id);
if(rj.data&&rj.data.length)S.juros=rj.data.map(r=>({id:r.id,data:r.data,valor:Number(r.valor)}));
if(rc2.data&&rc2.data.length)S.contas=rc2.data.map(r=>({id:r.id,item:r.item,mes:r.mes,valor:Number(r.valor),status:r.status}));
save();if(!silent)toast('☁️ Dados sincronizados!');refreshPage();
}catch(e){console.warn('Supabase pull error:',e.message);if(!silent)toast('Erro ao sincronizar: '+e.message,true)}}
async function sbSeedAll(silent){
if(!SB)return silent?0:toast('Supabase não configurado!',true);
if(!silent&&!confirm('Enviar todos os dados da planilha para o Supabase?'))return;
if(!silent)toast('☁️ Enviando dados...');
try{
const up=async(t,rows)=>{const r=await SB.from(t).upsert(rows,{onConflict:'id'});if(r.error)throw new Error(t+': '+r.error.message);return r};
await Promise.all([
up('compras',S.compras.map(c=>({id:c.id,quantidade:c.quantidade,material:c.material,valor:c.valor,forma:c.forma,parcelas:c.parcelas,fornecedor:c.fornecedor,data:c.data,pagador:c.pagador,status:c.status,categoria:c.categoria}))),
up('mao_de_obra',S.maoDeObra.map(c=>({id:c.id,data:c.data,valor:c.valor,descricao:c.descricao,status:c.status}))),
up('documentos',S.documentos.map(c=>({id:c.id,servico:c.servico,valor:c.valor,data:c.data,forma:c.forma,obs:c.obs}))),
up('juros',S.juros.map(c=>({id:c.id||uid(),data:c.data,valor:c.valor}))),
up('contas',S.contas.map(c=>({id:c.id||uid(),item:c.item,mes:c.mes,valor:c.valor,status:c.status})))]);
if(!silent)toast('✅ Dados enviados ao Supabase!');
return 1;
}catch(e){if(!silent)toast('Erro: '+e.message,true);return 0}}
async function sbAutoSeed(){
if(!SB)return;
try{
const r=await SB.from('compras').select('id',{count:'exact',head:true});
if(r.count===0){console.log('Supabase vazio — enviando dados iniciais...');await sbSeedAll(true)}
else{await sbPullAll(true)}
}catch(e){console.warn('autoSeed:',e.message)}}
// ============================================
let S=JSON.parse(JSON.stringify(SEED));
let SAVED=JSON.parse(localStorage.getItem('obra-facil-v2')||'null')||{};
if(SAVED.compras)S.compras=SAVED.compras;
if(SAVED.maoDeObra)S.maoDeObra=SAVED.maoDeObra;
if(SAVED.documentos)S.documentos=SAVED.documentos;
if(SAVED.parcelasPagas)S.parcelasPagas=SAVED.parcelasPagas;

// Limpeza automática: remove linhas de resumo antigas (TOTAL, SALDO) salvas no navegador
const _badRow=r=>!!(r&&r.data&&typeof r.data==='string'&&r.data.trim()!==''&&!/^\d{4}-\d{2}-\d{2}$/.test(r.data.trim()));
['compras','maoDeObra','documentos'].forEach(k=>{S[k]=(S[k]||[]).filter(r=>!_badRow(r))});

const CATEGORIAS=["Fundação","Estrutura","Alvenaria","Laje","Cobertura","Madeira/Formas","Elétrica","Hidráulica","Acabamento","Pintura","Serviços","Outros"];
const FORMAS={cartao:"Cartão",pix:"PIX",dinheiro:"Dinheiro",boleto:"Boleto",outro:"Outro"};
const uid=()=>(typeof crypto!=='undefined'&&crypto.randomUUID)?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const r=Math.random()*16|0;return(c==='x'?r:(r&0x3|0x8)).toString(16)});
function closeMenu(){document.querySelector('.nav-menu')?.classList.remove('open')}
function toggleNav(){const n=document.querySelector('.nav-menu');if(n)n.classList.toggle('open')}
const save=()=>localStorage.setItem('obra-facil-v2',JSON.stringify({compras:S.compras,maoDeObra:S.maoDeObra,documentos:S.documentos,parcelasPagas:S.parcelasPagas}));
const brl=v=>'R$ '+Number(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const brlS=v=>v>=1000?'R$ '+(v/1000).toLocaleString('pt-BR',{maximumFractionDigits:1})+' mil':brl(v);
const dataBR=d=>d?new Date(d+'T12:00:00').toLocaleDateString('pt-BR'):'—';
function toast(msg,err,undo){const t=document.getElementById('toast');t.innerHTML=msg+(undo?' <button class="undo" onclick="'+undo+'()">Desfazer</button>':'');t.className='toast show'+(err?' error':'');setTimeout(()=>t.className='toast',4000)}
function show(id,btn){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById('page-'+id).classList.add('active');document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));if(btn)btn.classList.add('active');
const titles={dashboard:'Painel',compras:'Compras',parcelas:'Parcelas',maoobra:'Mão de Obra',documentos:'Documentos',financiamento:'Financiamento',juros:'Juros & acerto',divisao:'Rateio Matheus'};document.getElementById('pageTitle').textContent=titles[id]||id;
setTimeout(()=>{destroyAll();if(id==='dashboard')renderDash();else if(id==='compras')renderCompras();else if(id==='parcelas')renderParcelas();else if(id==='maoobra')renderMO();else if(id==='documentos')renderDocs();else if(id==='financiamento')renderFin();else if(id==='juros')renderJuros();else if(id==='divisao')renderSplit()},50)}

// CHART MANAGEMENT
let _ch={};
if(typeof Chart!=='undefined'){Chart.defaults.color='#a1a1aa';Chart.defaults.borderColor='rgba(63,63,70,.6)';Chart.defaults.font.family="Inter,system-ui,sans-serif";Chart.defaults.font.size=11;Chart.defaults.plugins.tooltip.backgroundColor='#18181b';Chart.defaults.plugins.tooltip.borderColor='#3f3f46';Chart.defaults.plugins.tooltip.borderWidth=1;Chart.defaults.plugins.tooltip.padding=10;Chart.defaults.plugins.tooltip.titleColor='#fafafa';Chart.defaults.plugins.tooltip.bodyColor='#a1a1aa';Chart.defaults.plugins.tooltip.cornerRadius=8}
function barGrad(hex){return(c)=>{const{ctx,chartArea}=c.chart;if(!chartArea)return hex;const g=ctx.createLinearGradient(0,chartArea.bottom,0,chartArea.top);g.addColorStop(0,hex+'33');g.addColorStop(.6,hex+'cc');g.addColorStop(1,hex);return g}}
function mk(id,cfg){if(typeof Chart==='undefined')return;const el=document.getElementById(id);if(!el)return;if(_ch[id]){try{_ch[id].destroy()}catch(e){}}_ch[id]=new Chart(el,cfg)}
function destroyAll(){Object.values(_ch).forEach(c=>{try{c.destroy()}catch(e){}});_ch={}}

// PARCELAS
function addMonths(iso,n){const d=new Date(iso+'T12:00:00');d.setMonth(d.getMonth()+n);return d.toISOString().slice(0,10)}
function gerarParcelas(){
const out=[];const hoje=new Date().toISOString().slice(0,10);
for(const c of S.compras){if(c.forma!=='cartao'||!c.data)continue;const n=Math.max(1,c.parcelas||1);const base=Math.floor((c.valor/n)*100)/100;
for(let i=1;i<=n;i++){const val=i===n?Math.round((c.valor-base*(n-1))*100)/100:base;const venc=addMonths(c.data,i);const id=c.id+'-'+i;const paga=S.parcelasPagas.includes(id)||venc<hoje;
out.push({id,compraId:c.id,desc:c.material,forn:c.fornecedor,num:i,total:n,valor:val,venc,status:paga?'pago':(venc<hoje?'atrasado':'pendente')})}}
return out.sort((a,b)=>a.venc.localeCompare(b.venc))}

function somaPor(arr,fn,val){const m=new Map();for(const i of arr)m.set(fn(i),(m.get(fn(i))||0)+val(i));return[...m.entries()].map(([nome,total])=>({nome,total})).sort((a,b)=>b.total-a.total)}

// RENDER DASHBOARD
function renderDash(){
const mat=S.compras.reduce((a,c)=>a+c.valor,0),mao=S.maoDeObra.reduce((a,c)=>a+c.valor,0),docs=S.documentos.reduce((a,c)=>a+c.valor,0);
const juros=(S.juros||[]).reduce((a,c)=>a+(c.valor||0),0)+(S.contas||[]).reduce((a,c)=>a+(c.valor||0),0);
const total=mat+mao+docs+juros;
const parc=gerarParcelas();const aPagar=parc.filter(p=>p.status!=='pago');const totPagar=aPagar.reduce((a,p)=>a+p.valor,0);
const ref=S.obra.area*S.obra.valorM2;
document.getElementById('heroTotal').textContent=brl(total);
document.getElementById('heroSub').textContent=S.obra.area+' m² · obra financiada · '+S.compras.length+' compras · '+S.maoDeObra.length+' pagamentos';
document.getElementById('statsGrid').innerHTML=`
<div class="stat"><div class="label">🧱 Materiais</div><div class="value">${brlS(mat)}</div><div class="hint">${S.compras.length} lançamentos</div></div>
<div class="stat ${mao>ref?'danger':''}"><div class="label">👷 Mão de obra</div><div class="value">${brlS(mao)}</div><div class="hint">Ref. ${brlS(ref)} · saldo ${brlS(ref-mao)}</div></div>
<div class="stat primary"><div class="label">💳 A pagar no cartão</div><div class="value">${brlS(totPagar)}</div><div class="hint">${aPagar.length} parcelas futuras</div></div>
<div class="stat"><div class="label">📋 Docs + Juros</div><div class="value">${brlS(docs+juros)}</div><div class="hint">financiamento, taxas e contas</div></div>`;

const porMes=somaPor(S.compras.filter(c=>c.data),c=>c.data.slice(0,7),c=>c.valor).sort((a,b)=>a.nome.localeCompare(b.nome));
const lbl=porMes.map(m=>{const[y,mo]=m.nome.split('-');return['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][parseInt(mo)-1]+'/'+y.slice(2)});
mk('chartMes',{type:'bar',data:{labels:lbl,datasets:[{data:porMes.map(m=>m.total),backgroundColor:barGrad('#8b5cf6'),borderRadius:[6,6,0,0]}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brlS(v)}}}}});

mk('chartCat',{type:'doughnut',data:{labels:['Materiais','Mão de obra','Documentação','Juros/Contas'],datasets:[{data:[mat,mao,docs,juros],backgroundColor:['#8b5cf6','#10b981','#3b82f6','#f59e0b'],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}},cutout:'60%'}});

const pag=somaPor(S.compras,c=>FORMAS[c.forma]||'Outro',c=>c.valor).slice(0,6);
mk('chartPag',{type:'bar',data:{labels:pag.map(p=>p.nome),datasets:[{data:pag.map(p=>p.total),backgroundColor:barGrad('#3b82f6'),borderRadius:8}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{callback:v=>brlS(v)}}}}});

const forn=somaPor(S.compras,c=>c.fornecedor||'Sem fornecedor',c=>c.valor).slice(0,8);
mk('chartForn',{type:'bar',data:{labels:forn.map(f=>f.nome),datasets:[{data:forn.map(f=>f.total),backgroundColor:barGrad('#10b981'),borderRadius:8}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{callback:v=>brlS(v)}}}}});
}

// RENDER COMPRAS
let _sortC={col:'data',asc:false};
function sortC(col){_sortC.asc=_sortC.col===col?!_sortC.asc:true;_sortC.col=col;renderCompras()}
function renderCompras(){
const q=(document.getElementById('cq').value||'').toLowerCase(),forn=document.getElementById('cforn').value,cat=document.getElementById('ccat').value,forma=document.getElementById('cforma').value;
const fornOpts=[...new Set(S.compras.map(c=>c.fornecedor).filter(Boolean))].sort();
document.getElementById('cforn').innerHTML='<option value="">Todos fornecedores</option>'+fornOpts.map(f=>`<option>${f}</option>`).join('');
document.getElementById('ccat').innerHTML='<option value="">Todas etapas</option>'+CATEGORIAS.map(c=>`<option>${c}</option>`).join('');
document.getElementById('cforma').innerHTML='<option value="">Todas formas</option>'+Object.entries(FORMAS).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');

let items=S.compras.map((c,i)=>({...c,_i:i})).filter(c=>(!q||c.material.toLowerCase().includes(q))&&(!forn||c.fornecedor===forn)&&(!cat||c.categoria===cat)&&(!forma||c.forma===forma));
items.sort((a,b)=>{let va=a[_sortC.col],vb=b[_sortC.col];if(_sortC.col==='valor'){va=Number(va)||0;vb=Number(vb)||0}else{va=String(va||'');vb=String(vb||'')}return _sortC.asc?(va>vb?1:-1):(va<vb?1:-1)});
const total=items.reduce((s,c)=>s+c.valor,0);
document.getElementById('comprasBody').innerHTML=items.map(c=>`<tr>
<td>${dataBR(c.data)}${c._new?'<span class="new-badge">NOVO</span>':''}</td>
<td><b>${c.material}</b>${c.quantidade?' <span style="color:var(--text2)">· '+c.quantidade+'</span>':''}</td>
<td style="font-weight:600;color:var(--accent2)">${brl(c.valor)}</td>
<td>${c.fornecedor||'—'}</td>
<td>${FORMAS[c.forma]||c.forma}${c.forma==='cartao'&&c.parcelas>1?' '+c.parcelas+'x':''}</td>
<td><span class="badge cat">${c.categoria}</span></td>
<td><span class="badge ${c.status}">${c.status}</span></td>
<td><div style="display:flex;gap:4px">
<button class="btn btn-ghost btn-icon" onclick="editEntry('compra',${c._i})" title="Editar">✏️</button>
<button class="btn btn-ghost btn-icon" onclick="dupCompra(${c._i})" title="Duplicar">📋</button>
<button class="btn btn-ghost btn-icon" onclick="delCompra(${c._i})" title="Excluir">🗑️</button></div></td></tr>`).join('');
document.getElementById('comprasCards').innerHTML=items.length===0?'<div style="padding:24px;color:var(--text2);text-align:center">Nenhuma compra encontrada</div>':items.map(c=>`<div class="mcard">
<div class="mi"><div class="mt">${c.material}${c._new?' <span class="new-badge">NOVO</span>':''}</div>
<div class="ms">${dataBR(c.data)}${c.quantidade?' · '+c.quantidade:''}<br>${c.fornecedor||'Sem fornecedor'} · ${FORMAS[c.forma]||c.forma}${c.forma==='cartao'&&c.parcelas>1?' '+c.parcelas+'x':''} · <span class="badge cat">${c.categoria}</span></div></div>
<div class="mr"><div class="mv">${brl(c.valor)}</div>
<div class="ma"><span class="badge ${c.status}">${c.status}</span>
<button class="btn btn-ghost btn-icon" onclick="editEntry('compra',${c._i})">✏️</button>
<button class="btn btn-ghost btn-icon" onclick="delCompra(${c._i})">🗑️</button></div></div></div>`).join('');
}

function dupCompra(i){const c={...S.compras[i],id:uid(),data:new Date().toISOString().slice(0,10),_new:true};S.compras.unshift(c);save();renderCompras();toast('📋 Compra duplicada!')}
let _lastDeleted=null;
function delCompra(i){const c=S.compras[i];_lastDeleted={arr:'compras',item:JSON.parse(JSON.stringify(c))};S.compras.splice(i,1);save();renderCompras();toast('🗑️ Excluído!',false,'undoLast')}

// RENDER PARCELAS
function renderParcelas(){
const parc=gerarParcelas();const abertas=parc.filter(p=>p.status!=='pago');
const hoje=new Date();
const somaAte=d=>{const lim=new Date(hoje.getTime()+d*864e5).toISOString().slice(0,10);return abertas.filter(p=>p.venc<=lim).reduce((a,p)=>a+p.valor,0)};
document.getElementById('parcelasStats').innerHTML=`
<div class="stat primary"><div class="label">⏰ Próx. 7 dias</div><div class="value">${brl(somaAte(7))}</div></div>
<div class="stat"><div class="label">📅 Próx. 30 dias</div><div class="value">${brl(somaAte(30))}</div></div>
<div class="stat"><div class="label">📆 Próx. 90 dias</div><div class="value">${brl(somaAte(90))}</div></div>`;
document.getElementById('parcCount').textContent=abertas.length+' abertas';

const porMes=somaPor(abertas,p=>p.venc.slice(0,7),p=>p.valor).sort((a,b)=>a.nome.localeCompare(b.nome));
const MN=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
document.getElementById('parcPorMes').innerHTML=porMes.length===0?'<p style="color:var(--text2);padding:8px 0">Nenhuma fatura em aberto 🎉</p>':porMes.map(m=>{const[y,mo]=m.nome.split('-');return`<div class="pmes-row"><span>${MN[parseInt(mo)-1]} De ${y}</span><b>${brl(m.total)}</b></div>`}).join('');

document.getElementById('parcelasList').innerHTML=abertas.length===0?'<p style="padding:16px 0;color:var(--text2)">Tudo quitado! 🎉</p>':abertas.map(p=>`
<div class="parc-item">
<div class="pi-main">
<div class="pi-title">${p.desc}</div>
<div class="pi-sub">${p.forn||'—'} · parcela ${p.num}/${p.total} · vence ${dataBR(p.venc)}</div>
</div>
<span class="badge ${p.status}">${p.status}</span>
<div class="pi-valor">${brl(p.valor)}</div>
<button class="btn-pago" onclick="pagarParc('${p.id}')" title="Marcar como paga">✓ Pago</button>
</div>`).join('');
}
function pagarParc(id){if(!S.parcelasPagas.includes(id)){S.parcelasPagas.push(id);sbPush('parcelas_pagas',{parcela_id:id})}save();renderParcelas();toast('✅ Parcela quitada!')}

// RENDER MÃO DE OBRA
function renderMO(){
const tot=S.maoDeObra.reduce((a,c)=>a+c.valor,0);const ref=S.obra.area*S.obra.valorM2;
document.getElementById('moStats').innerHTML=`
<div class="stat ${tot>ref?'danger':''}"><div class="label">👷 Total pago</div><div class="value">${brlS(tot)}</div><div class="hint">${S.maoDeObra.length} pagamentos</div></div>
<div class="stat"><div class="label">📐 Referência (m²)</div><div class="value">${brlS(ref)}</div><div class="hint">${S.obra.area}m² × ${brl(S.obra.valorM2)}</div></div>
<div class="stat ${tot>ref?'danger':''}"><div class="label">💵 Saldo</div><div class="value">${brlS(ref-tot)}</div><div class="hint">${tot>ref?'Acima da referência':'Dentro do orçamento'}</div></div>`;

const porMes=somaPor(S.maoDeObra.filter(c=>c.data),c=>c.data.slice(0,7),c=>c.valor).sort((a,b)=>a.nome.localeCompare(b.nome));
const lbl=porMes.map(m=>{const[y,mo]=m.nome.split('-');return['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][parseInt(mo)-1]});
let cum=0;const acum=porMes.map(m=>{cum+=m.total;return cum});
mk('chartMo',{type:'bar',data:{labels:lbl,datasets:[{data:porMes.map(m=>m.total),backgroundColor:barGrad('#ef4444'),borderRadius:[6,6,0,0]}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brlS(v)}}}}});
mk('chartMoAcum',{type:'line',data:{labels:lbl,datasets:[{data:acum,borderColor:'#10b981',backgroundColor:'rgba(16,185,129,.1)',fill:true,tension:.4,pointBackgroundColor:'#10b981'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brlS(v)}}}}});

document.getElementById('moBody').innerHTML=S.maoDeObra.slice().reverse().map((c,ri)=>{const i=S.maoDeObra.length-1-ri;return`<tr><td>${dataBR(c.data)}</td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor)}</td><td>${c.descricao||'—'}</td><td><span class="badge ${c.status}">${c.status}</span></td><td><button class="btn btn-ghost btn-icon" onclick="editEntry('maoobra',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('maoDeObra',${i})">🗑️</button></td></tr>`}).join('');
document.getElementById('moCards').innerHTML=S.maoDeObra.slice().reverse().map((c,ri)=>{const i=S.maoDeObra.length-1-ri;return`<div class="mcard"><div class="mi"><div class="mt">${c.descricao||'Pagamento'}</div><div class="ms">${dataBR(c.data)}</div></div><div class="mr"><div class="mv">${brl(c.valor)}</div><div class="ma"><span class="badge ${c.status}">${c.status}</span><button class="btn btn-ghost btn-icon" onclick="editEntry('maoobra',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('maoDeObra',${i})">🗑️</button></div></div></div>`}).join('');
}

// RENDER DOCS
function renderDocs(){
const tot=S.documentos.reduce((a,c)=>a+c.valor,0);
document.getElementById('docStats').innerHTML=`<div class="stat"><div class="label">📋 Total documentação</div><div class="value">${brlS(tot)}</div><div class="hint">${S.documentos.length} serviços</div></div>`;
const porMes=somaPor(S.documentos.filter(c=>c.data),c=>c.data.slice(0,7),c=>c.valor).sort((a,b)=>a.nome.localeCompare(b.nome));
const lbl=porMes.map(m=>{const[y,mo]=m.nome.split('-');return['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][parseInt(mo)-1]});
mk('chartDoc',{type:'bar',data:{labels:lbl,datasets:[{data:porMes.map(m=>m.total),backgroundColor:barGrad('#6366f1'),borderRadius:[6,6,0,0]}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brlS(v)}}}}});
const top=S.documentos.filter(c=>c.valor).sort((a,b)=>b.valor-a.valor).slice(0,8);
mk('chartDocPie',{type:'pie',data:{labels:top.map(c=>(c.servico||'').substring(0,20)),datasets:[{data:top.map(c=>c.valor),backgroundColor:['#8b5cf6','#10b981','#3b82f6','#f59e0b','#ef4444','#ec4899','#14b8a6','#f97316'],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{font:{size:10}}}}}});
document.getElementById('docBody').innerHTML=S.documentos.map((c,i)=>`<tr><td><b>${c.servico}</b></td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor)}</td><td>${dataBR(c.data)}</td><td>${c.forma||'—'}</td><td><button class="btn btn-ghost btn-icon" onclick="editEntry('doc',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('documentos',${i})">🗑️</button></td></tr>`).join('');
document.getElementById('docCards').innerHTML=S.documentos.map((c,i)=>`<div class="mcard"><div class="mi"><div class="mt">${c.servico}</div><div class="ms">${dataBR(c.data)}${c.forma?' · '+c.forma:''}</div></div><div class="mr"><div class="mv">${brl(c.valor)}</div><div class="ma"><button class="btn btn-ghost btn-icon" onclick="editEntry('doc',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('documentos',${i})">🗑️</button></div></div></div>`).join('');
}

// RENDER FIN (financiamento)
function renderFin(){
const juros=S.juros||[],contas=S.contas||[];
const totJ=juros.reduce((a,c)=>a+(c.valor||0),0),totC=contas.reduce((a,c)=>a+(c.valor||0),0);
document.getElementById('finStats').innerHTML=`
<div class="stat"><div class="label">🏦 Financiamento</div><div class="value">${brlS(totJ)}</div><div class="hint">${juros.length} parcelas</div></div>
<div class="stat"><div class="label">💡 Contas</div><div class="value">${brlS(totC)}</div><div class="hint">${contas.length} contas</div></div>
<div class="stat primary"><div class="label">📊 Total fixo</div><div class="value">${brlS(totJ+totC)}</div><div class="hint">custos mensais da obra</div></div>`;

const jl=juros.map(c=>{if(!c.data)return'-';const[,m,d]=c.data.split('-');return d+'/'+m});
mk('chartFin',{type:'line',data:{labels:jl,datasets:[{label:'Parcela',data:juros.map(c=>c.valor||0),borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,.1)',fill:true,tension:.3,pointBackgroundColor:'#ef4444'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brl(v)}}}}});

const uc={};contas.forEach(c=>{uc[c.item]=(uc[c.item]||0)+(c.valor||0)});
mk('chartContas',{type:'bar',data:{labels:Object.keys(uc),datasets:[{data:Object.values(uc),backgroundColor:['#3b82f6','#f59e0b','#10b981','#8b5cf6'],borderRadius:8}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brl(v)}}}}});

document.getElementById('finBody').innerHTML=juros.map((c,i)=>`<tr><td>${dataBR(c.data)}</td><td style="font-weight:600;color:var(--red)">${brl(c.valor||0)}</td><td><button class="btn btn-ghost btn-icon" onclick="delEntry('juros',${i})">🗑️</button></td></tr>`).join('');
document.getElementById('finCards').innerHTML=juros.map((c,i)=>`<div class="mcard"><div class="mi"><div class="mt">Parcela</div><div class="ms">${dataBR(c.data)}</div></div><div class="mr"><div class="mv" style="color:var(--red)">${brl(c.valor||0)}</div><div class="ma"><button class="btn btn-ghost btn-icon" onclick="delEntry('juros',${i})">🗑️</button></div></div></div>`).join('');
document.getElementById('contasBody').innerHTML=contas.map((c,i)=>`<tr><td>${c.item}</td><td>${c.mes||'—'}</td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor||0)}</td><td><span class="badge ${c.status||'pago'}">${c.status||'pago'}</span></td><td><button class="btn btn-ghost btn-icon" onclick="delEntry('contas',${i})">🗑️</button></td></tr>`).join('');
document.getElementById('contasCards').innerHTML=contas.map((c,i)=>`<div class="mcard"><div class="mi"><div class="mt">${c.item}</div><div class="ms">${c.mes||'—'}</div></div><div class="mr"><div class="mv">${brl(c.valor||0)}</div><div class="ma"><span class="badge ${c.status||'pago'}">${c.status||'pago'}</span><button class="btn btn-ghost btn-icon" onclick="delEntry('contas',${i})">🗑️</button></div></div></div>`).join('');
}

// RENDER JUROS & ACERTO
function renderJuros(){
const juros=(S.juros||[]).slice().sort((a,b)=>(a.data||'').localeCompare(b.data||''));
const contas=S.contas||[],rateio=S.rateio||[],rd=S.resumoDivisao||{};
const totJ=juros.reduce((a,c)=>a+(c.valor||0),0);
const totC=contas.reduce((a,c)=>a+(c.valor||0),0);
const totD=rateio.reduce((a,c)=>a+(c.valor||0),0);
const atual=juros.length?juros[juros.length-1].valor||0:0;
const primeiro=juros.length?juros[0].valor||0:0;
const ter=rd['VALOR TERRENO']||0,esc=rd['DESPESAS ESCRITURA']||0,adi=rd['ADIANTAMENTO']||0;
const devido=rd['VALOR DEVIDO']||(ter-esc-adi);

document.getElementById('jStats').innerHTML=`
<div class="stat primary"><div class="label">🏦 Juros pagos</div><div class="value">${brl(totJ)}</div><div class="hint">${juros.length} meses</div></div>
<div class="stat"><div class="label">📈 Juros atual/mês</div><div class="value" style="color:var(--accent2)">${brl(atual)}</div><div class="hint">começou em ${brl(primeiro)}</div></div>
<div class="stat"><div class="label">💡 Água, luz e IPTU</div><div class="value">${brl(totC)}</div><div class="hint">${contas.length} contas pagas</div></div>
<div class="stat danger"><div class="label">🤝 Devido a Matheus</div><div class="value">${brl(devido)}</div></div>`;

const MS=['jan.','fev.','mar.','abr.','mai.','jun.','jul.','ago.','set.','out.','nov.','dez.'];
const jl=juros.map(c=>{if(!c.data)return'';const[y,m]=c.data.split('-');return MS[parseInt(m)-1]+' de '+y.slice(2)});
mk('chartJuros',{type:'line',data:{labels:jl,datasets:[{label:'Juros',data:juros.map(c=>c.valor||0),borderColor:'#8b5cf6',backgroundColor:barGrad('#8b5cf6'),fill:true,tension:.35,pointBackgroundColor:'#8b5cf6',pointRadius:3,borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' '+brl(c.parsed.y)}}},scales:{y:{beginAtZero:true,ticks:{callback:v=>v}},x:{ticks:{maxRotation:0,autoSkip:true,maxTicksLimit:12}}}}});

document.getElementById('acertoBox').innerHTML=`
<div class="jc-item"><span>Valor do terreno</span><span class="jc-val">${brl(ter)}</span></div>
<div class="jc-item neg"><span>(-) Metade das despesas de escritura</span><span class="jc-val">-${brl(esc)}</span></div>
<div class="jc-item neg"><span>(-) Adiantamento</span><span class="jc-val">-${brl(adi)}</span></div>
<div class="jc-total"><span>Valor devido</span><span class="jc-val">${brl(devido)}</span></div>`;

document.getElementById('despBox').innerHTML=rateio.map(c=>`
<div class="jc-row"><div class="jc-name">${c.item||'—'}<span class="jc-date">${dataBR(c.data)}</span></div>
<div class="jc-valor">${brl(c.valor||0)}</div></div>`).join('')+`
<div class="jc-totrow"><span>Total</span><span class="jc-valor">${brl(totD)}</span></div>`;
}

// RENDER SPLIT (rateio Matheus)
function renderSplit(){
const rd=S.resumoDivisao||{};
document.getElementById('splitBox').innerHTML=`<h3>🤝 Resumo do Rateio</h3>
<div class="split-item"><span>💰 Valor do Terreno</span><strong>${brl(rd['VALOR TERRENO']||35000)}</strong></div>
<div class="split-item"><span>📋 Despesas Escritura</span><strong>${brl(rd['DESPESAS ESCRITURA']||1579.66)}</strong></div>
<div class="split-item"><span>🤝 Adiantamento</span><strong>${brl(rd['ADIANTAMENTO']||2000)}</strong></div>
<div class="split-item"><span>💵 Caio Deve</span><strong>${brl(rd['VALOR DEVIDO']||31420.34)}</strong></div>
<div class="split-item"><span>🔄 Retorno Matheus</span><strong style="color:var(--green)">${brl(rd['RETORNO']||579.66)}</strong></div>`;
mk('chartSplit',{type:'doughnut',data:{labels:['Terreno (Caio)','Metade Escritura','Adiantamento'],datasets:[{data:[17500,1579.66/2,2000],backgroundColor:['#8b5cf6','#f59e0b','#10b981'],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}},cutout:'60%'}});
document.getElementById('splitBody').innerHTML=(S.rateio||[]).map(c=>`<tr><td>${c.item||'—'}</td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor||0)}</td><td>${dataBR(c.data)}</td></tr>`).join('');
document.getElementById('splitCards').innerHTML=(S.rateio||[]).map(c=>`<div class="mcard"><div class="mi"><div class="mt">${c.item||'—'}</div><div class="ms">${dataBR(c.data)}</div></div><div class="mr"><div class="mv">${brl(c.valor||0)}</div></div></div>`).join('');
}

// MODAL
let modalType=null,editIdx=null;
const MAP={compra:'compras',maoobra:'maoDeObra',doc:'documentos'};
function openModal(type,ref){
modalType=type;editIdx=(ref===undefined||ref===null)?null:Number(ref);
const ed=editIdx!==null;
const m=document.getElementById('modal');const t=document.getElementById('modalTitle');const b=document.getElementById('modalBody');
if(type==='compra'){t.innerHTML=ed?'✏️ Editar compra':'🧱 Nova compra';b.innerHTML=`
<div class="form-group"><label>Material</label><input id="f_material" placeholder="Ex: Cimento CP-II"></div>
<div class="form-row"><div class="form-group"><label>Quantidade</label><input id="f_quantidade" placeholder="Ex: 10 sacos"></div>
<div class="form-group"><label>Valor (R$)</label><input id="f_valor" type="number" step="0.01"></div></div>
<div class="form-row"><div class="form-group"><label>Forma de pagamento</label><select id="f_forma">${Object.entries(FORMAS).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select></div>
<div class="form-group"><label>Nº Parcelas (se cartão)</label><input id="f_parcelas" type="number" value="1" min="1"></div></div>
<div class="form-row"><div class="form-group"><label>Fornecedor</label><input id="f_fornecedor" placeholder="Ex: Imperio Construções"></div>
<div class="form-group"><label>Data</label><input id="f_data" type="date" value="${new Date().toISOString().slice(0,10)}"></div></div>
<div class="form-row"><div class="form-group"><label>Etapa</label><select id="f_categoria">${CATEGORIAS.map(c=>`<option>${c}</option>`).join('')}</select></div>
<div class="form-group"><label>Status</label><select id="f_status"><option value="pago">Pago</option><option value="pendente">Pendente</option></select></div></div>`}
else if(type==='maoobra'){t.innerHTML=ed?'✏️ Editar pagamento':'👷 Novo pagamento';b.innerHTML=`
<div class="form-row"><div class="form-group"><label>Data</label><input id="f_data" type="date" value="${new Date().toISOString().slice(0,10)}"></div>
<div class="form-group"><label>Valor (R$)</label><input id="f_valor" type="number" step="0.01"></div></div>
<div class="form-group"><label>Descrição</label><input id="f_descricao" placeholder="Ex: ROGERIO, PINTURA..."></div>
<div class="form-group"><label>Status</label><select id="f_status"><option value="pago">Pago</option><option value="pendente">Pendente</option></select></div>`}
else if(type==='doc'){t.innerHTML=ed?'✏️ Editar serviço':'📋 Novo serviço';b.innerHTML=`
<div class="form-group"><label>Serviço</label><input id="f_servico" placeholder="Ex: ITBI, Alvará..."></div>
<div class="form-row"><div class="form-group"><label>Valor (R$)</label><input id="f_valor" type="number" step="0.01"></div>
<div class="form-group"><label>Data</label><input id="f_data" type="date" value="${new Date().toISOString().slice(0,10)}"></div></div>
<div class="form-group"><label>Forma de pagamento</label><input id="f_forma" placeholder="Ex: PIX CAIO, BB..."></div>`}
m.classList.add('open');
if(ed)prefillForm(type,editIdx);
}
function prefillForm(type,idx){
const it=S[MAP[type]][idx];if(!it)return;
const set=(k,val)=>{const e=document.getElementById('f_'+k);if(e)e.value=(val===null||val===undefined)?'':val};
if(type==='compra'){set('material',it.material);set('quantidade',it.quantidade);set('valor',it.valor);set('forma',it.forma);set('parcelas',it.parcelas||1);set('fornecedor',it.fornecedor);set('data',it.data);set('categoria',it.categoria);set('status',it.status)}
else if(type==='maoobra'){set('data',it.data);set('valor',it.valor);set('descricao',it.descricao);set('status',it.status)}
else if(type==='doc'){set('servico',it.servico);set('valor',it.valor);set('data',it.data);set('forma',it.forma)}
}
function editEntry(type,idx){openModal(type,idx)}
function closeModal(){document.getElementById('modal').classList.remove('open');modalType=null;editIdx=null}
function refreshPage(){let cur=((document.querySelector('.page.active')||{}).id||'').replace('page-','');
if(cur==='compras')renderCompras();else if(cur==='maoobra')renderMO();else if(cur==='documentos')renderDocs();else if(cur==='financiamento')renderFin();else if(cur==='dashboard')renderDash();else if(cur==='parcelas')renderParcelas();else if(cur==='juros')renderJuros();else if(cur==='divisao')renderSplit()}

function saveEntry(){
const g=id=>{const e=document.getElementById('f_'+id);return e?e.value.trim():''};
const v=id=>{const e=document.getElementById('f_'+id);return e?Number(e.value)||0:0};
try{
if(editIdx!==null){
const arr=MAP[modalType];const it=S[arr][editIdx];if(!it){closeModal();return}
if(modalType==='compra'){const mat=g('material');if(!mat)return toast('Informe o material!',true);
Object.assign(it,{quantidade:g('quantidade'),material:mat,valor:v('valor'),forma:g('forma'),parcelas:v('parcelas')||1,fornecedor:g('fornecedor'),data:g('data'),status:g('status'),categoria:g('categoria')});
sbUpdate('compras',it.id,{quantidade:it.quantidade,material:it.material,valor:it.valor,forma:it.forma,parcelas:it.parcelas,fornecedor:it.fornecedor,data:it.data,pagador:it.pagador,status:it.status,categoria:it.categoria})}
else if(modalType==='maoobra'){const val=v('valor');if(!val)return toast('Informe o valor!',true);
Object.assign(it,{data:g('data'),valor:val,descricao:g('descricao'),status:g('status')});
sbUpdate('mao_de_obra',it.id,{data:it.data,valor:it.valor,descricao:it.descricao,status:it.status})}
else if(modalType==='doc'){const srv=g('servico');if(!srv)return toast('Informe o serviço!',true);
Object.assign(it,{servico:srv,valor:v('valor'),data:g('data'),forma:g('forma')});
sbUpdate('documentos',it.id,{servico:it.servico,valor:it.valor,data:it.data,forma:it.forma,obs:it.obs})}
save();closeModal();refreshPage();toast('✅ Alterações salvas!');return;
}
if(modalType==='compra'){const mat=g('material');if(!mat)return toast('Informe o material!',true);
const item={id:uid(),quantidade:g('quantidade'),material:mat,valor:v('valor'),forma:g('forma'),parcelas:v('parcelas')||1,fornecedor:g('fornecedor'),data:g('data'),pagador:'CAIO',status:g('status'),categoria:g('categoria'),_new:true};
S.compras.unshift(item);sbPush('compras',{id:item.id,quantidade:item.quantidade,material:item.material,valor:item.valor,forma:item.forma,parcelas:item.parcelas,fornecedor:item.fornecedor,data:item.data,pagador:item.pagador,status:item.status,categoria:item.categoria});toast('✅ Compra salva!')}
else if(modalType==='maoobra'){const val=v('valor');if(!val)return toast('Informe o valor!',true);
const item={id:uid(),data:g('data'),valor:val,descricao:g('descricao'),status:g('status'),_new:true};
S.maoDeObra.unshift(item);sbPush('mao_de_obra',{id:item.id,data:item.data,valor:item.valor,descricao:item.descricao,status:item.status});toast('✅ Pagamento salvo!')}
else if(modalType==='doc'){const srv=g('servico');if(!srv)return toast('Informe o serviço!',true);
const item={id:uid(),servico:srv,valor:v('valor'),data:g('data'),forma:g('forma'),obs:null,_new:true};
S.documentos.unshift(item);sbPush('documentos',{id:item.id,servico:item.servico,valor:item.valor,data:item.data,forma:item.forma,obs:item.obs});toast('✅ Serviço salvo!')}
save();closeModal();refreshPage();
}catch(e){toast('Erro: '+e.message,true)}
}

function delEntry(arr,i){const item=S[arr][i];_lastDeleted={arr:arr,idx:i,item:JSON.parse(JSON.stringify(item))};S[arr].splice(i,1);save();
const sbTable={maoDeObra:'mao_de_obra',documentos:'documentos',juros:'juros',contas:'contas',compras:'compras'};
if(sbTable[arr]&&item.id)sbDelete(sbTable[arr],item.id);
const renders={maoDeObra:renderMO,documentos:renderDocs,juros:renderFin,contas:renderFin};(renders[arr]||renderCompras)();
toast('🗑️ Excluído!',false,'undoLast')}
function undoLast(){if(!_lastDeleted)return;const{arr,item}=_lastDeleted;if(arr==='compras')S.compras.unshift(item);else S[arr].splice(_lastDeleted.idx,0,item);_lastDeleted=null;save();
const renders={maoDeObra:renderMO,documentos:renderDocs,juros:renderFin,contas:renderFin};(renders[arr]||renderCompras)();toast('↩️ Restaurado!')}

function resetAll(){localStorage.removeItem('obra-facil-v2');S=JSON.parse(JSON.stringify(SEED));toast('🔄 Dados restaurados!')}

// Offline: os dados continuam salvos no aparelho, só não sincroniza
if(typeof window!=='undefined'){
window.addEventListener('offline',()=>toast('📴 Sem internet — seus dados continuam salvos neste aparelho',true));
window.addEventListener('online',()=>{toast('📶 Internet de volta! Sincronizando...');sbPullAll(false)});
if(navigator.onLine===false)toast('📴 Sem internet — seus dados continuam salvos neste aparelho',true);
}

function exportCSV(){let csv='Categoria;Material;Valor;Forma;Data;Fornecedor;Status;Etapa\n';
S.compras.forEach(c=>{csv+=`Compra;${c.material};${c.valor};${c.forma}${c.parcelas>1?c.parcelas+'x':''};${c.data||''};${c.fornecedor||''};${c.status};${c.categoria}\n`});
S.maoDeObra.forEach(c=>{csv+=`MaoObra;;;${c.valor};;${c.data};${c.status};;${c.descricao||''}\n`});
S.documentos.forEach(c=>{csv+=`Doc;${c.servico};${c.valor};;${c.data||''};;;${c.forma||''}\n`});
const blob=new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='obra_casa_caio.csv';a.click();toast('📥 CSV exportado!')}

// INIT
show('dashboard');
if(SB){setTimeout(()=>sbAutoSeed(),800)}
// Força a página a ficar encostada na esquerda (evita corte lateral)
function resetX(){if(window.scrollX>0||document.documentElement.scrollLeft>0)window.scrollTo(0,window.scrollY||0)}
window.addEventListener('load',()=>{history.scrollRestoration='manual';resetX()});
setInterval(resetX,1500);
window.addEventListener('scroll',()=>{if(window.scrollX>0)window.scrollTo(0,window.scrollY)});
</script>
</body>
</html>"""

html = html.replace("__DATA__", data_js)

out = r"C:\Users\Odair\Documents\App Caio\index.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"App unificado: {out}")
print(f"Tamanho: {len(html)//1024} KB")
