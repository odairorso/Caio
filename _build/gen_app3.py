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
        "status": "pago" if str(c.get("status") or "").strip().upper() == "PAGO" else "pendente", "categoria": "Outros"
    })

maoDeObra = []
for i, c in enumerate(data.get("mao_obra", [])):
    if _is_summary(c.get("data")):
        continue  # pula linhas TOTAL/SALDO da planilha
    maoDeObra.append({"id": _uid("mo:" + str(i)), "data": c.get("data") or "", "valor": c.get("valor") or 0,
        "descricao": c.get("quem") or c.get("forma") or "", "status": "pago" if str(c.get("status") or "").strip().upper() == "PAGO" else "pendente"})

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

# Obra de demonstração (dados fictícios) — serve para ver como fica com mais de uma obra
demo = {
    "compras": [
        {"id": _uid("demo:c1"), "quantidade": "1.000", "material": "TIJOLO 8 FUROS", "valor": 1250.00,
         "forma": "pix", "parcelas": 1, "fornecedor": "OLARIA NAVIRAÍ", "data": "2026-09-05",
         "pagador": "ODAIR", "status": "pago", "categoria": "Outros"},
        {"id": _uid("demo:c2"), "quantidade": "50", "material": "CIMENTO CP-II", "valor": 2100.00,
         "forma": "cartao", "parcelas": 6, "fornecedor": "IMPÉRIO CONSTRUÇÕES", "data": "2026-09-10",
         "pagador": "ODAIR", "status": "pago", "categoria": "Outros"},
        {"id": _uid("demo:c3"), "quantidade": "3 m³", "material": "AREIA MÉDIA", "valor": 480.00,
         "forma": "dinheiro", "parcelas": 1, "fornecedor": "AREIAL NAVIRAÍ", "data": "2026-09-12",
         "pagador": "ODAIR", "status": "pendente", "categoria": "Outros"},
        {"id": _uid("demo:c4"), "quantidade": "120", "material": "TELHA CERÂMICA", "valor": 3480.00,
         "forma": "cartao", "parcelas": 10, "fornecedor": "AÇO TELHAS DOURADOS", "data": "2026-09-20",
         "pagador": "ODAIR", "status": "pendente", "categoria": "Outros"},
        {"id": _uid("demo:c5"), "quantidade": "18 L", "material": "TINTA ACRÍLICA", "valor": 620.00,
         "forma": "pix", "parcelas": 1, "fornecedor": "DESTRO", "data": "2026-10-02",
         "pagador": "ODAIR", "status": "pago", "categoria": "Outros"},
    ],
    "maoDeObra": [
        {"id": _uid("demo:m1"), "data": "2026-09-08", "valor": 3500.00, "descricao": "Pedreiro · alvenaria", "status": "pago"},
        {"id": _uid("demo:m2"), "data": "2026-09-25", "valor": 2500.00, "descricao": "Equipe · laje", "status": "pago"},
        {"id": _uid("demo:m3"), "data": "2026-10-05", "valor": 1800.00, "descricao": "Ajudante", "status": "pendente"},
    ],
    "documentos": [
        {"id": _uid("demo:d1"), "servico": "ALVARÁ DE CONSTRUÇÃO", "valor": 850.00, "data": "2026-08-20", "forma": "PIX", "obs": ""},
        {"id": _uid("demo:d2"), "servico": "ART DO ENGENHEIRO", "valor": 1200.00, "data": "2026-08-25", "forma": "PIX", "obs": ""},
    ],
    "parcelasPagas": [],
    "juros": [
        {"id": _uid("demo:j1"), "data": "2026-09-10", "valor": 410.00},
        {"id": _uid("demo:j2"), "data": "2026-10-10", "valor": 410.00},
    ],
    "contas": [
        {"id": _uid("demo:u1"), "item": "ÁGUA", "mes": "SET", "valor": 95.00, "status": "PAGO"},
        {"id": _uid("demo:u2"), "item": "LUZ", "mes": "SET", "valor": 180.00, "status": "PAGO"},
    ],
    "rateio": [],
    "resumoDivisao": {},
    "orcamento": {"materiais": 45000, "mao": 30000, "doc": 8000, "juros": 5000, "contas": 2000},
    "diario": [{"id": _uid("demo:n1"), "data": "2026-09-26", "titulo": "Laje concretada",
                "texto": "Concretagem concluída com 12 m³. Próxima etapa: cura de 7 dias e início da alvenaria do pavimento superior."}],
}

seed = {"compras": compras, "maoDeObra": maoDeObra, "documentos": documentos,
    "parcelasPagas": [], "juros": juros, "contas": contas,
    "rateio": rateio, "resumoDivisao": data.get("resumo_divisao", {}),
    "orcamento": {"materiais": 105000, "mao": 70000, "doc": 16000, "juros": 0, "contas": 2500},
    "diario": [],
    "obra": {"area": 72, "valorM2": 1800},
    "obras": [
        {"id": "casa-caio", "nome": "Casa Caio", "local": "Naviraí · MS", "area": 72, "valorM2": 1800},
        {"id": "casa-odair-teste", "nome": "Casa Odair Teste", "local": "Naviraí · MS", "area": 60, "valorM2": 1500},
    ],
    "obraAtiva": "casa-caio",
    "dados": {"casa-odair-teste": demo}}

data_js = json.dumps(seed, ensure_ascii=False)

html = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Obra Fácil — Casa Caio</title>
<meta name="description" content="Controle de custos da obra da Casa Caio: compras, parcelas do cartão, mão de obra, documentação, financiamento e rateio.">
<meta name="theme-color" content="#09090b">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Obra Fácil">
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
.sync-chip{font-size:15px;line-height:1;padding:6px 10px;border-radius:20px;background:var(--card3);border:1px solid var(--border);cursor:default;user-select:none}
.sync-chip.ok{color:var(--green)}
.sync-chip.off{color:var(--orange)}
.sync-chip.err{color:var(--red)}
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
.parc-sep{position:sticky;top:0;z-index:2;display:flex;align-items:center;justify-content:space-between;gap:8px;background:var(--card);padding:10px 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text2);border-bottom:1px solid rgba(39,39,42,.5)}
.parc-sep .btn{text-transform:none;letter-spacing:0;font-size:11px;padding:4px 10px}
.pi-main{flex:1;min-width:0}
.pi-title{font-size:13.5px;font-weight:600;text-transform:uppercase;letter-spacing:.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pi-sub{font-size:11.5px;color:var(--text2);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pi-valor{font-size:14.5px;font-weight:700;white-space:nowrap}
.btn-pago{display:inline-flex;align-items:center;gap:5px;background:var(--card2);border:1px solid var(--border);color:var(--text);padding:6px 13px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .2s;white-space:nowrap}
.btn-pago:hover{background:var(--green);border-color:var(--green);color:#fff}
@media(max-width:768px){.parc-item{flex-wrap:wrap;gap:10px}.pi-main{flex:1 1 100%}.pi-valor{margin-left:auto}.parc-items{max-height:none;overflow:visible}.pmes-list,.parc-items{padding-left:16px;padding-right:16px}}
/* OBRAS */
.obra-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:18px}
.obra-acoes{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.obra-select{background:var(--card2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-family:inherit;font-size:13.5px;font-weight:600;padding:9px 12px;outline:none;max-width:220px}
.obra-select:focus{border-color:var(--accent)}
.obra-selo{display:inline-block;margin-top:8px;font-size:11px;color:var(--text2);border:1px solid var(--border);border-radius:20px;padding:3px 9px}
.obra-head h2{font-size:24px;font-weight:800;letter-spacing:-.5px}
.obra-head p{font-size:12.5px;color:var(--text2);margin-top:4px}
.subtabs{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:22px;overflow-x:auto;scrollbar-width:none}
.subtabs::-webkit-scrollbar{display:none}
.subtab{background:none;border:none;border-bottom:2px solid transparent;color:var(--text2);font-family:inherit;font-size:13.5px;font-weight:600;padding:10px 14px;cursor:pointer;white-space:nowrap;transition:color .2s,border-color .2s}
.subtab:hover{color:var(--text)}
.subtab.active{color:var(--accent2);border-bottom-color:var(--accent)}
.obra-pane{display:none}
.obra-pane.active{display:block}
.orc-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px;margin-bottom:12px}
.orc-top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.orc-name{font-size:14.5px;font-weight:700}
.orc-nums{font-size:12.5px;color:var(--text2);display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:10px}
.orc-nums b{color:var(--text)}
.prog{height:8px;border-radius:6px;background:var(--card3);overflow:hidden}
.prog-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .3s}
.prog-fill.over{background:linear-gradient(90deg,#b91c1c,var(--red))}
.diario-item{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px;margin-bottom:12px}
.diario-data{font-size:11.5px;color:var(--text2);margin-bottom:6px}
.diario-titulo{font-size:15px;font-weight:700;margin-bottom:6px}
.diario-texto{font-size:13.5px;color:var(--text2);line-height:1.55;white-space:pre-wrap;word-break:break-word}
.gasto-acoes{display:flex;gap:4px;justify-content:flex-end;white-space:nowrap}
.orc-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.orc-head p{font-size:12.5px;color:var(--text2)}
@media(max-width:768px){.obra-head h2{font-size:20px}.subtab{padding:9px 10px;font-size:12.5px}.orc-card{padding:16px}.orc-head{align-items:flex-start}}
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
<button class="nav-btn" onclick="show('obras',this);closeMenu()"><span class="ico">🏗️</span>Obras</button>
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
<div class="actions">
<span class="sync-chip" id="syncChip" title="Status da sincronização">☁️</span>
<button class="btn btn-ghost btn-icon" onclick="baixarBackup()" title="Baixar backup dos dados">⬇️</button>
</div>
</div>

<div class="content" role="main">
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
<input type="text" id="cq" placeholder="🔍 Buscar material..." oninput="buscaCompras()">
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

<!-- OBRAS (visao unificada) -->
<div id="page-obras" class="page">
<div class="obra-head">
<div><h2 id="obraNome">Casa Caio</h2><p id="obraResumoSub">Obra em Naviraí · MS</p><span id="obraSelo" class="obra-selo" style="display:none"></span></div>
<div class="obra-acoes">
<select id="obraSeletor" class="obra-select" onchange="trocarObra(this.value)" title="Trocar de obra"></select>
<button class="btn btn-secondary" onclick="openObraNova()">➕ Nova obra</button>
<button class="btn btn-ghost btn-icon" onclick="openObraEditar()" title="Editar esta obra">✏️</button>
<button class="btn btn-ghost btn-icon" onclick="excluirObra()" title="Excluir esta obra">🗑️</button>
</div>
</div>
<div class="subtabs">
<button class="subtab active" onclick="obraTab('resumo',this)">Resumo</button>
<button class="subtab" onclick="obraTab('gastos',this)">Gastos</button>
<button class="subtab" onclick="obraTab('orcamento',this)">Orçamento</button>
<button class="subtab" onclick="obraTab('parcelas',this)">Parcelas</button>
<button class="subtab" onclick="obraTab('socio',this)">Sócio</button>
<button class="subtab" onclick="obraTab('diario',this)">Diário</button>
</div>

<div id="obra-resumo" class="obra-pane active">
<div class="stats" id="obraStats"></div>
<div class="grid2">
<div class="chart-box"><h3>📊 Gasto por mês</h3><canvas id="chartObraMes"></canvas></div>
<div class="chart-box"><h3>🍩 Gasto por categoria</h3><canvas id="chartObraCat"></canvas></div>
</div>
<div class="chart-box" style="height:400px"><h3>🏪 Gasto por fornecedor — top 10</h3><canvas id="chartObraForn"></canvas></div>
</div>

<div id="obra-gastos" class="obra-pane">
<div class="filters">
<input type="text" id="gq" placeholder="🔍 Material ou fornecedor..." oninput="buscaGastos()">
<select id="gcat" onchange="renderObraGastos()"><option value="">Todas categorias</option><option>Materiais</option><option>Mão de obra</option><option>Documentação e taxas</option><option>Financiamento</option><option>Contas de água e luz</option></select>
<select id="gsit" onchange="renderObraGastos()"><option value="">Todas situações</option><option value="pago">Pago</option><option value="pendente">Pendente</option></select>
<button class="btn btn-primary" onclick="openModal('compra')">➕ Novo gasto</button>
</div>
<div class="stats" id="gastosStats"></div>
<div class="table-box"><div class="table-wrap"><table>
<thead><tr><th>Item</th><th>Fornecedor</th><th>Data</th><th>Valor</th><th>Situação</th><th></th></tr></thead>
<tbody id="gastosBody"></tbody></table></div><div class="mobile-list" id="gastosCards"></div></div>
</div>

<div id="obra-orcamento" class="obra-pane">
<div class="orc-head">
<p id="orcSub"></p>
<button class="btn btn-secondary" onclick="openOrcamento()">✏️ Editar orçamento</button>
</div>
<div id="orcList"></div>
</div>

<div id="obra-parcelas" class="obra-pane">
<div class="stats" id="obraParcStats"></div>
<div class="table-box"><div class="header"><h3>💳 Parcelas em aberto</h3><span class="count" id="obraParcCount"></span></div>
<div class="parc-items" id="obraParcList"></div></div>
</div>

<div id="obra-socio" class="obra-pane">
<div class="stats" id="obraSocioStats"></div>
<div class="table-box"><div class="header"><h3>🤝 Despesas divididas com Matheus</h3></div>
<div class="table-wrap"><table>
<thead><tr><th>Item</th><th>Valor</th><th>Data</th></tr></thead>
<tbody id="obraSocioBody"></tbody></table></div><div class="mobile-list" id="obraSocioCards"></div></div>
</div>

<div id="obra-diario" class="obra-pane">
<div class="filters">
<button class="btn btn-primary" onclick="openDiario()">➕ Novo registro</button>
<span class="parc-sub" style="margin:0">Anotações do andamento da obra (salvas neste aparelho e no backup)</span>
</div>
<div id="diarioList"></div>
</div>
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
// A tabela "obras" (varias obras na nuvem) pode ainda nao existir: o app detecta sozinho
let SB_TEM_OBRAS=false;
// ============================================
// RELOGIO LOCAL — toISOString usa UTC e, no Brasil, vira o dia depois das 21h
// ============================================
const hojeISO=()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')};
const maisDias=d=>{const t=new Date();t.setHours(12,0,0,0);t.setDate(t.getDate()+d);return t.getFullYear()+'-'+String(t.getMonth()+1).padStart(2,'0')+'-'+String(t.getDate()).padStart(2,'0')};

// ============================================
// FILA DE PENDENCIAS — o que nao conseguiu chegar na nuvem
// ============================================
const PEND_KEY='obra-facil-pend';
const lerPend=()=>{try{const p=JSON.parse(localStorage.getItem(PEND_KEY)||'null');return{del:p&&Array.isArray(p.del)?p.del:[],add:p&&Array.isArray(p.add)?p.add:[]}}catch(e){return{del:[],add:[]}}};
let PEND=lerPend();
const gravarPend=()=>{try{localStorage.setItem(PEND_KEY,JSON.stringify(PEND))}catch(e){}};
const pendDel=(t,col,val)=>{PEND.del=PEND.del.filter(x=>!(x.t===t&&x.col===col&&x.v===val));PEND.add=PEND.add.filter(x=>!(x.t===t&&x.col===col&&x.v===val));PEND.del.push({t:t,col:col,v:val});gravarPend()};
const pendOk=(t,col,val)=>{const n=PEND.del.length;PEND.del=PEND.del.filter(x=>!(x.t===t&&x.col===col&&x.v===val));if(PEND.del.length!==n)gravarPend()};
const pendAdd=(t,col,val)=>{PEND.add=PEND.add.filter(x=>!(x.t===t&&x.col===col&&x.v===val));PEND.del=PEND.del.filter(x=>!(x.t===t&&x.col===col&&x.v===val));PEND.add.push({t:t,col:col,v:val});gravarPend()};
const pendAddOk=(t,col,val)=>{const n=PEND.add.length;PEND.add=PEND.add.filter(x=>!(x.t===t&&x.col===col&&x.v===val));if(PEND.add.length!==n)gravarPend()};

const marcarSujo=id=>{if(!id)return;let mudou=false;
for(const k of ['compras','maoDeObra','documentos','juros','contas']){for(const it of (S[k]||[])){if(it&&it.id===id&&!it._dirty){it._dirty=true;mudou=true}}}
if(mudou)save()};
const limparSujo=id=>{if(!id)return;for(const k of ['compras','maoDeObra','documentos','juros','contas']){for(const it of (S[k]||[])){if(it&&it.id===id){it._dirty=false;it._new=false}}}
try{document.querySelectorAll('[data-novo="'+String(id)+'"]').forEach(e=>e.remove())}catch(e){}};

async function sbPush(table,payload){
// As tabelas antigas guardam so a Casa Caio. Obras novas vao para a tabela "obras".
if(S.obraAtiva!=='casa-caio')return null;
const rows=Array.isArray(payload)?payload:[payload];
if(!SB){rows.forEach(r=>r&&marcarSujo(r.id));return null}
try{
const todosTemId=rows.length>0&&rows.every(r=>r&&r.id);
const limpos=rows.map(cloudRow);
const q=todosTemId?SB.from(table).upsert(limpos,{onConflict:'id'}):SB.from(table).insert(limpos);
const{data,error}=await q;if(error)throw error;
rows.forEach(r=>r&&limparSujo(r.id));
return data}catch(e){console.warn('Supabase push error:',e.message);rows.forEach(r=>r&&marcarSujo(r.id));marcarSinc('err');return null}}
const cloudRow=o=>{const r={...o};delete r._new;delete r._i;delete r._dirty;return r};
async function sbUpdate(table,id,payload){
if(S.obraAtiva!=='casa-caio')return null;
if(!SB){marcarSujo(id);return null}
try{const{data,error}=await SB.from(table).update(payload).eq('id',id);if(error)throw error;limparSujo(id);return data}
catch(e){console.warn('Supabase update error:',e.message);marcarSujo(id);return null}}
async function sbDelete(table,id){
if(S.obraAtiva!=='casa-caio')return null;
if(!SB){pendDel(table,'id',id);return null}
try{const{error}=await SB.from(table).delete().eq('id',id);if(error)throw error;pendOk(table,'id',id);return true}
catch(e){console.warn('Supabase delete error:',e.message);pendDel(table,'id',id);return null}}
async function reenviarPendencias(){
if(!SB)return 0;
let ok=0;
// 1) o que ficou para INSERIR (ex: parcela paga sem internet)
for(const p of (PEND.add||[]).slice()){
try{const{error}=await SB.from(p.t).upsert({[p.col]:p.v},{onConflict:p.col});if(error)throw error;pendAddOk(p.t,p.col,p.v);ok++}
catch(e){console.warn('pendencia (add) nao resolvida:',p.t,p.v,e.message)}}
// 2) o que ficou para APAGAR
for(const p of PEND.del.slice()){
try{const{error}=await SB.from(p.t).delete().eq(p.col,p.v);if(error)throw error;pendOk(p.t,p.col,p.v);ok++}
catch(e){console.warn('pendencia (del) nao resolvida:',p.t,p.v,e.message)}}
return ok}
// Mantem o que existe apenas no aparelho (lancado sem internet) e reenvia.
// Edicao local pendente vence a versao da nuvem.
function mesclar(nuvem,local,tabela){
const mapa=new Map();
for(const r of nuvem)mapa.set(r.id,r);
const reenviar=[];
for(const r of (local||[])){
if(!r||!r.id)continue;
if(mapa.has(r.id)){
if(r._dirty){mapa.set(r.id,r);reenviar.push(r)}
}else if(r._dirty||r._new){mapa.set(r.id,r);reenviar.push(r)}
}
if(reenviar.length)sbPush(tabela,reenviar.map(cloudRow));
return [...mapa.values()]}
async function sbPullAll(silent){
if(!SB)return false;
if(S.obraAtiva!=='casa-caio')return false;
try{
const[rc,rm,rd,rp,rj,rc2]=await Promise.all([
SB.from('compras').select('*'),SB.from('mao_de_obra').select('*'),SB.from('documentos').select('*'),
SB.from('parcelas_pagas').select('*'),SB.from('juros').select('*'),SB.from('contas').select('*')]);
const erro=[rc,rm,rd,rp,rj,rc2].find(r=>r&&r.error);
if(erro)throw new Error(erro.error.message);
const compras=(rc.data||[]).map(r=>({id:r.id,quantidade:r.quantidade,material:r.material,valor:Number(r.valor),forma:r.forma,parcelas:r.parcelas,fornecedor:r.fornecedor,data:r.data,pagador:r.pagador,status:r.status,categoria:r.categoria}));
const mao=(rm.data||[]).map(r=>({id:r.id,data:r.data,valor:Number(r.valor),descricao:r.descricao,status:r.status}));
const docs=(rd.data||[]).map(r=>({id:r.id,servico:r.servico,valor:Number(r.valor),data:r.data,forma:r.forma,obs:r.obs}));
const juros=(rj.data||[]).map(r=>({id:r.id,data:r.data,valor:Number(r.valor)}));
const contas=(rc2.data||[]).map(r=>({id:r.id,item:r.item,mes:r.mes,valor:Number(r.valor),status:r.status}));
const pagas=(rp.data||[]).map(r=>r.parcela_id);
S.compras=mesclar(compras,S.compras,'compras');
S.maoDeObra=mesclar(mao,S.maoDeObra,'mao_de_obra');
S.documentos=mesclar(docs,S.documentos,'documentos');
S.juros=mesclar(juros,S.juros,'juros');
S.contas=mesclar(contas,S.contas,'contas');
const pendParc=new Set(PEND.del.filter(p=>p.t==='parcelas_pagas').map(p=>p.v));
const compraIds=new Set(S.compras.map(c=>c.id));
S.parcelasPagas=[...new Set([...pagas,...(S.parcelasPagas||[])])].filter(id=>{
if(pendParc.has(id))return false;
const base=String(id).replace(/-\d+$/,'');
return compraIds.has(base)||base===String(id)});
save();marcarSinc('ok');if(!silent)toast('☁️ Dados sincronizados!');refreshPage();return true;
}catch(e){console.warn('Supabase pull error:',e.message);marcarSinc('err');if(!silent)toast('Erro ao sincronizar: '+e.message,true);return false}}
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
if(S.parcelasPagas.length){const rp2=await SB.from('parcelas_pagas').upsert(S.parcelasPagas.map(x=>({parcela_id:x})),{onConflict:'parcela_id'});if(rp2.error)throw new Error('parcelas_pagas: '+rp2.error.message)}
try{localStorage.setItem('obra-facil-semeado','1')}catch(e){}
if(!silent)toast('✅ Dados enviados ao Supabase!');
return 1;
}catch(e){if(!silent)toast('Erro: '+e.message,true);return 0}}
async function detectarTabelaObras(){
if(!SB)return false;
try{const r=await SB.from('obras').select('id').limit(1);if(r.error)throw r.error;SB_TEM_OBRAS=true}
catch(e){SB_TEM_OBRAS=false}
return SB_TEM_OBRAS}

// Mescla por id: o que foi editado no aparelho (_dirty) vence a nuvem
function mesclarObra(nuvem,local){
const mapa=new Map();
for(const r of (nuvem||[])){if(r&&r.id)mapa.set(r.id,r)}
for(const r of (local||[])){if(!r||!r.id)continue;if(r._dirty||!mapa.has(r.id))mapa.set(r.id,r)}
return [...mapa.values()]}

function pacoteDaNuvem(d,atual){
atual=atual||{};
return {compras:mesclarObra(d.compras,atual.compras),
maoDeObra:mesclarObra(d.maoDeObra,atual.maoDeObra),
documentos:mesclarObra(d.documentos,atual.documentos),
parcelasPagas:[...new Set([...(atual.parcelasPagas||[]),...(d.parcelasPagas||[])])],
juros:mesclarObra(d.juros,atual.juros),
contas:mesclarObra(d.contas,atual.contas),
rateio:mesclarObra(d.rateio,atual.rateio),
resumoDivisao:d.resumoDivisao||atual.resumoDivisao||{},
orcamento:d.orcamento||atual.orcamento||ORCAMENTO_VAZIO(),
diario:mesclarObra(d.diario,atual.diario)}}

async function puxarObrasNuvem(silent){
if(!SB||!SB_TEM_OBRAS)return false;
try{
const{data,error}=await SB.from('obras').select('*');if(error)throw error;
for(const o of (data||[])){
const local=S.obras.find(x=>x.id===o.id);
if(!local)S.obras.push({id:o.id,nome:o.nome||'Obra',local:o.local||'',area:Number(o.area)||0,valorM2:Number(o.valor_m2)||0});
else{local.nome=o.nome||local.nome;local.local=o.local||local.local;if(Number(o.area))local.area=Number(o.area);if(Number(o.valor_m2))local.valorM2=Number(o.valor_m2)}
if(o.id==='casa-caio'||!o.dados)continue;
if(o.id===S.obraAtiva)continue; // a obra aberta na tela tem prioridade
S.dados[o.id]=pacoteDaNuvem(o.dados,S.dados[o.id]);
}
S.obras.forEach(o=>{if(!S.dados[o.id])S.dados[o.id]=PACOTE_VAZIO()});
save();if(!silent)toast('☁️ Obras sincronizadas!');return true;
}catch(e){console.warn('puxarObras:',e.message);return false}}

async function puxarObraDaNuvem(id){
if(!SB||!SB_TEM_OBRAS||id==='casa-caio')return;
try{
const{data,error}=await SB.from('obras').select('*').eq('id',id).limit(1);if(error)throw error;
const o=(data||[])[0];if(!o||!o.dados)return;
S.dados[id]=pacoteDaNuvem(o.dados,S.dados[id]);
if(S.obraAtiva===id){aplicarObraAtiva();save();renderObras()}
}catch(e){console.warn('puxarObra:',e.message)}}

async function enviarObra(o){
if(!SB||!SB_TEM_OBRAS||!o)return false;
try{
if(o.id===S.obraAtiva)sincronizarAtiva();
const dados=o.id==='casa-caio'?{}:(S.dados[o.id]||{});
const{error}=await SB.from('obras').upsert({id:o.id,nome:o.nome,local:o.local||'',area:o.area||0,valor_m2:o.valorM2||0,dados:dados,atualizado_em:new Date().toISOString()},{onConflict:'id'});
if(error)throw error;
marcarSinc('ok');return true;
}catch(e){console.warn('enviarObra:',e.message);marcarSinc('err');return false}}

let _tPushObra=null;
function agendarPushObra(){
if(!SB||!SB_TEM_OBRAS)return;
const o=obraAtual();
if(!o||o.id==='casa-caio')return;
clearTimeout(_tPushObra);
_tPushObra=setTimeout(()=>{sincronizarAtiva();enviarObra(o)},1200)}

async function sbAutoSeed(){
if(!SB)return;
try{
await detectarTabelaObras();
if(S.obraAtiva==='casa-caio'){
const r=await SB.from('compras').select('id',{count:'exact',head:true});
if(r.error)throw r.error;
const jaSemeou=localStorage.getItem('obra-facil-semeado');
if(r.count===0&&!jaSemeou){console.log('Supabase vazio — enviando dados iniciais...');await sbSeedAll(true)}
else{await sbPullAll(true)}
}
if(SB_TEM_OBRAS)await puxarObrasNuvem(true);
await reenviarPendencias();
}catch(e){console.warn('autoSeed:',e.message)}}
// ============================================
// OBRA ATIVA — cada obra tem o seu proprio conjunto de dados
// ============================================
const CAMPOS_OBRA=['compras','maoDeObra','documentos','parcelasPagas','juros','contas','rateio','resumoDivisao','orcamento','diario'];
const ORCAMENTO_VAZIO=()=>({materiais:0,mao:0,doc:0,juros:0,contas:0});
const PACOTE_VAZIO=()=>({compras:[],maoDeObra:[],documentos:[],parcelasPagas:[],juros:[],contas:[],rateio:[],resumoDivisao:{},orcamento:ORCAMENTO_VAZIO(),diario:[]});
let S=JSON.parse(JSON.stringify(SEED));
if(!S.obras||!S.obras.length)S.obras=[{id:'casa-caio',nome:'Casa Caio',local:'Naviraí · MS',area:(S.obra&&S.obra.area)||72,valorM2:(S.obra&&S.obra.valorM2)||1800}];
if(!S.dados)S.dados={};
if(!S.obraAtiva)S.obraAtiva=S.obras[0].id;
const pacoteCasa=()=>({compras:S.compras,maoDeObra:S.maoDeObra,documentos:S.documentos,parcelasPagas:S.parcelasPagas,juros:S.juros,contas:S.contas,rateio:S.rateio,resumoDivisao:S.resumoDivisao,orcamento:S.orcamento,diario:S.diario});
if(!S.dados['casa-caio'])S.dados['casa-caio']=pacoteCasa();

let SAVED=JSON.parse(localStorage.getItem('obra-facil-v2')||'null')||{};
if(SAVED.dados&&SAVED.obras){
// formato novo (varias obras)
S.obras=SAVED.obras;
S.obraAtiva=SAVED.obraAtiva||SAVED.obras[0].id;
S.dados=SAVED.dados;
}else if(SAVED.compras||SAVED.maoDeObra||SAVED.documentos||SAVED.contas){
// formato antigo (um conjunto unico de dados): vira a Casa Caio
S.dados['casa-caio']={compras:SAVED.compras||S.compras,maoDeObra:SAVED.maoDeObra||S.maoDeObra,
documentos:SAVED.documentos||S.documentos,parcelasPagas:SAVED.parcelasPagas||S.parcelasPagas,
juros:SAVED.juros||S.juros,contas:SAVED.contas||S.contas,rateio:S.rateio,
resumoDivisao:S.resumoDivisao,orcamento:SAVED.orcamento||S.orcamento,diario:SAVED.diario||S.diario};
}
if(!S.obras.some(o=>o.id===S.obraAtiva))S.obraAtiva=S.obras[0].id;
S.obras.forEach(o=>{if(!S.dados[o.id])S.dados[o.id]=PACOTE_VAZIO()});
function sincronizarAtiva(){S.dados[S.obraAtiva]={compras:S.compras,maoDeObra:S.maoDeObra,documentos:S.documentos,parcelasPagas:S.parcelasPagas,juros:S.juros,contas:S.contas,rateio:S.rateio,resumoDivisao:S.resumoDivisao,orcamento:S.orcamento,diario:S.diario}}
function aplicarObraAtiva(){const d=S.dados[S.obraAtiva]||PACOTE_VAZIO();
S.compras=d.compras||[];S.maoDeObra=d.maoDeObra||[];S.documentos=d.documentos||[];
S.parcelasPagas=d.parcelasPagas||[];S.juros=d.juros||[];S.contas=d.contas||[];
S.rateio=d.rateio||[];S.resumoDivisao=d.resumoDivisao||{};
S.orcamento=d.orcamento||ORCAMENTO_VAZIO();S.diario=d.diario||[]}
function obraAtual(){return (S.obras||[]).find(o=>o.id===S.obraAtiva)||S.obras[0]}
aplicarObraAtiva();

// Limpeza automatica: remove apenas linhas de resumo antigas (TOTAL/SALDO), sem tocar no resto
const _resumo=r=>{const t=String((r&&(r.material||r.descricao||r.servico))||'').trim().toUpperCase();return /^(TOTAL|SUBTOTAL|TOTAL GERAL|SALDO|SALDO FINAL)\b/.test(t)};
const _badRow=r=>!!(r&&_resumo(r)&&!(r.data&&/^\d{4}-\d{2}-\d{2}$/.test(String(r.data).trim())));
Object.keys(S.dados).forEach(id=>{
['compras','maoDeObra','documentos'].forEach(k=>{S.dados[id][k]=(S.dados[id][k]||[]).filter(r=>!_badRow(r))});
});
aplicarObraAtiva();

const CATEGORIAS=["Fundação","Estrutura","Alvenaria","Laje","Cobertura","Madeira/Formas","Elétrica","Hidráulica","Acabamento","Pintura","Serviços","Outros"];
const FORMAS={cartao:"Cartão",pix:"PIX",dinheiro:"Dinheiro",boleto:"Boleto",outro:"Outro"};
const uid=()=>(typeof crypto!=='undefined'&&crypto.randomUUID)?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const r=Math.random()*16|0;return(c==='x'?r:(r&0x3|0x8)).toString(16)});
function closeMenu(){document.querySelector('.nav-menu')?.classList.remove('open')}
function toggleNav(){const n=document.querySelector('.nav-menu');if(n)n.classList.toggle('open')}
let _saveAviso=false;
const save=()=>{try{sincronizarAtiva();localStorage.setItem('obra-facil-v2',JSON.stringify({versao:3,obras:S.obras,obraAtiva:S.obraAtiva,dados:S.dados}));agendarPushObra()}
catch(e){console.warn('save:',e.message);if(!_saveAviso){_saveAviso=true;try{toast('⚠️ Não consegui salvar neste aparelho. Faça um backup!',true)}catch(_){}}}};
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const brl=v=>'R$ '+Number(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const brlS=v=>v>=1000?'R$ '+(v/1000).toLocaleString('pt-BR',{maximumFractionDigits:1})+' mil':brl(v);
const dataBR=d=>d?new Date(d+'T12:00:00').toLocaleDateString('pt-BR'):'—';
function toast(msg,err,undo){const t=document.getElementById('toast');t.innerHTML=esc(msg)+(undo?' <button class="undo" onclick="'+undo+'()">Desfazer</button>':'');t.className='toast show'+(err?' error':'');setTimeout(()=>t.className='toast',4000)}
function show(id,btn){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById('page-'+id).classList.add('active');document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));if(btn)btn.classList.add('active');
const titles={dashboard:'Painel',obras:'Obras',compras:'Compras',parcelas:'Parcelas',maoobra:'Mão de Obra',documentos:'Documentos',financiamento:'Financiamento',juros:'Juros & acerto',divisao:'Rateio Matheus'};document.getElementById('pageTitle').textContent=titles[id]||id;
setTimeout(()=>{destroyAll();if(id==='dashboard')renderDash();else if(id==='obras')renderObras();else if(id==='compras')renderCompras();else if(id==='parcelas')renderParcelas();else if(id==='maoobra')renderMO();else if(id==='documentos')renderDocs();else if(id==='financiamento')renderFin();else if(id==='juros')renderJuros();else if(id==='divisao')renderSplit()},50)}

// CHART MANAGEMENT
let _ch={};
if(typeof Chart!=='undefined'){Chart.defaults.color='#a1a1aa';Chart.defaults.borderColor='rgba(63,63,70,.6)';Chart.defaults.font.family="Inter,system-ui,sans-serif";Chart.defaults.font.size=11;Chart.defaults.plugins.tooltip.backgroundColor='#18181b';Chart.defaults.plugins.tooltip.borderColor='#3f3f46';Chart.defaults.plugins.tooltip.borderWidth=1;Chart.defaults.plugins.tooltip.padding=10;Chart.defaults.plugins.tooltip.titleColor='#fafafa';Chart.defaults.plugins.tooltip.bodyColor='#a1a1aa';Chart.defaults.plugins.tooltip.cornerRadius=8}
function barGrad(hex){return(c)=>{const{ctx,chartArea}=c.chart;if(!chartArea)return hex;const g=ctx.createLinearGradient(0,chartArea.bottom,0,chartArea.top);g.addColorStop(0,hex+'33');g.addColorStop(.6,hex+'cc');g.addColorStop(1,hex);return g}}
function mk(id,cfg){if(typeof Chart==='undefined')return;const el=document.getElementById(id);if(!el)return;if(_ch[id]){try{_ch[id].destroy()}catch(e){}}_ch[id]=new Chart(el,cfg)}
function destroyAll(){Object.values(_ch).forEach(c=>{try{c.destroy()}catch(e){}});_ch={}}

// PARCELAS
function addMonths(iso,n){const[y,m,d]=String(iso).split('-').map(Number);const ultimoDia=new Date(y,m-1+n+1,0).getDate();const dt=new Date(y,m-1+n,Math.min(d,ultimoDia));return dt.getFullYear()+'-'+String(dt.getMonth()+1).padStart(2,'0')+'-'+String(dt.getDate()).padStart(2,'0')}
function gerarParcelas(){
const out=[];const hoje=hojeISO();
for(const c of S.compras){if(c.forma!=='cartao'||!c.data)continue;const n=Math.min(60,Math.max(1,Math.round(Number(c.parcelas)||1)));const base=Math.floor((c.valor/n)*100)/100;
for(let i=1;i<=n;i++){const val=i===n?Math.round((c.valor-base*(n-1))*100)/100:base;const venc=addMonths(c.data,i);const id=c.id+'-'+i;const paga=S.parcelasPagas.includes(id);
out.push({id,compraId:c.id,desc:c.material,forn:c.fornecedor,num:i,total:n,valor:val,venc,status:paga?'pago':(venc<hoje?'atrasado':'pendente')})}}
return out.sort((a,b)=>a.venc.localeCompare(b.venc))}

function somaPor(arr,fn,val){const m=new Map();for(const i of arr)m.set(fn(i),(m.get(fn(i))||0)+val(i));return[...m.entries()].map(([nome,total])=>({nome,total})).sort((a,b)=>b.total-a.total)}

// RENDER DASHBOARD
function renderDash(){
const mat=S.compras.reduce((a,c)=>a+c.valor,0),mao=S.maoDeObra.reduce((a,c)=>a+c.valor,0),docs=S.documentos.reduce((a,c)=>a+c.valor,0);
const juros=(S.juros||[]).reduce((a,c)=>a+(c.valor||0),0)+(S.contas||[]).reduce((a,c)=>a+(c.valor||0),0);
const total=mat+mao+docs+juros;
const parc=gerarParcelas();const aPagar=parc.filter(p=>p.status!=='pago');const totPagar=aPagar.reduce((a,p)=>a+p.valor,0);
const _hojeStr=hojeISO();
const nAtraso=aPagar.filter(p=>p.venc<_hojeStr).length;
const _obra=obraAtual()||{};const _area=Number(_obra.area)||0;const _vm2=Number(_obra.valorM2)||0;
const ref=_area*_vm2;
document.getElementById('heroTotal').textContent=brl(total);
document.getElementById('heroSub').textContent=(_obra.nome?_obra.nome+' · ':'')+(_area?_area+' m² · ':'')+S.compras.length+' compras · '+S.maoDeObra.length+' pagamentos';
document.getElementById('statsGrid').innerHTML=`
<div class="stat"><div class="label">🧱 Materiais</div><div class="value">${brlS(mat)}</div><div class="hint">${S.compras.length} lançamentos</div></div>
<div class="stat ${ref&&mao>ref?'danger':''}"><div class="label">👷 Mão de obra</div><div class="value">${brlS(mao)}</div><div class="hint">${ref?('Ref. '+brlS(ref)+' · saldo '+brlS(ref-mao)):'sem referência de m²'}</div></div>
<div class="stat primary"><div class="label">💳 A pagar no cartão</div><div class="value">${brlS(totPagar)}</div><div class="hint">${aPagar.length} em aberto${nAtraso?' · ⚠️ '+nAtraso+' atrasadas':''}</div></div>
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
// Espera o usuario parar de digitar antes de redesenhar (evita travar no celular)
let _tBusca=null;
function buscaCompras(){clearTimeout(_tBusca);_tBusca=setTimeout(renderCompras,220)}
function renderCompras(){
const q=(document.getElementById('cq').value||'').toLowerCase(),forn=document.getElementById('cforn').value,cat=document.getElementById('ccat').value,forma=document.getElementById('cforma').value;
const fornOpts=[...new Set(S.compras.map(c=>c.fornecedor).filter(Boolean))].sort();
document.getElementById('cforn').innerHTML='<option value="">Todos fornecedores</option>'+fornOpts.map(f=>`<option>${esc(f)}</option>`).join('');
document.getElementById('ccat').innerHTML='<option value="">Todas etapas</option>'+CATEGORIAS.map(c=>`<option>${c}</option>`).join('');
document.getElementById('cforma').innerHTML='<option value="">Todas formas</option>'+Object.entries(FORMAS).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');
// Restaura a selecao: os <select> foram remontados acima e voltariam para "Todos"
document.getElementById('cforn').value=forn;
document.getElementById('ccat').value=cat;
document.getElementById('cforma').value=forma;

let items=S.compras.map((c,i)=>({...c,_i:i})).filter(c=>(!q||String(c.material||'').toLowerCase().includes(q)||String(c.fornecedor||'').toLowerCase().includes(q))&&(!forn||c.fornecedor===forn)&&(!cat||c.categoria===cat)&&(!forma||c.forma===forma));
items.sort((a,b)=>{let va=a[_sortC.col],vb=b[_sortC.col];if(_sortC.col==='valor'){va=Number(va)||0;vb=Number(vb)||0}else{va=String(va||'');vb=String(vb||'')}return _sortC.asc?(va>vb?1:-1):(va<vb?1:-1)});
const total=items.reduce((s,c)=>s+c.valor,0);
document.getElementById('comprasBody').innerHTML=items.map(c=>`<tr>
<td>${dataBR(c.data)}${c._new?`<span class="new-badge" data-novo="${esc(c.id)}">NOVO</span>`:''}</td>
<td><b>${esc(c.material)}</b>${c.quantidade?' <span style="color:var(--text2)">· '+esc(c.quantidade)+'</span>':''}</td>
<td style="font-weight:600;color:var(--accent2)">${brl(c.valor)}</td>
<td>${esc(c.fornecedor||'—')}</td>
<td>${esc(FORMAS[c.forma]||c.forma)}${c.forma==='cartao'&&c.parcelas>1?' '+c.parcelas+'x':''}</td>
<td><span class="badge cat">${esc(c.categoria)}</span></td>
<td><span class="badge ${esc(c.status)}">${esc(c.status)}</span></td>
<td><div style="display:flex;gap:4px">
<button class="btn btn-ghost btn-icon" onclick="editEntry('compra',${c._i})" title="Editar">✏️</button>
<button class="btn btn-ghost btn-icon" onclick="dupCompra(${c._i})" title="Duplicar">📋</button>
<button class="btn btn-ghost btn-icon" onclick="delCompra(${c._i})" title="Excluir">🗑️</button></div></td></tr>`).join('');
document.getElementById('comprasCards').innerHTML=items.length===0?'<div style="padding:24px;color:var(--text2);text-align:center">Nenhuma compra encontrada</div>':items.map(c=>`<div class="mcard">
<div class="mi"><div class="mt">${esc(c.material)}${c._new?` <span class="new-badge" data-novo="${esc(c.id)}">NOVO</span>`:''}</div>
<div class="ms">${dataBR(c.data)}${c.quantidade?' · '+esc(c.quantidade):''}<br>${esc(c.fornecedor||'Sem fornecedor')} · ${esc(FORMAS[c.forma]||c.forma)}${c.forma==='cartao'&&c.parcelas>1?' '+c.parcelas+'x':''} · <span class="badge cat">${esc(c.categoria)}</span></div></div>
<div class="mr"><div class="mv">${brl(c.valor)}</div>
<div class="ma"><span class="badge ${esc(c.status)}">${esc(c.status)}</span>
<button class="btn btn-ghost btn-icon" onclick="editEntry('compra',${c._i})">✏️</button>
<button class="btn btn-ghost btn-icon" onclick="delCompra(${c._i})">🗑️</button></div></div></div>`).join('');
}

function dupCompra(i){const src=S.compras[i];if(!src)return;const c={...src,id:uid(),data:hojeISO(),_new:true};S.compras.unshift(c);save();renderCompras();sbPush('compras',cloudRow(c));toast('📋 Compra duplicada!')}
let _lastDeleted=null;
function delCompra(i){const c=S.compras[i];if(!c)return;
const n=Math.min(60,Math.max(1,Math.round(Number(c.parcelas)||1)));
const ids=[];for(let k=1;k<=n;k++)ids.push(c.id+'-'+k);
const pagasAntes=(S.parcelasPagas||[]).filter(x=>ids.includes(x));
_lastDeleted={arr:'compras',idx:i,item:JSON.parse(JSON.stringify(c)),parcelas:pagasAntes};
S.compras.splice(i,1);
S.parcelasPagas=(S.parcelasPagas||[]).filter(x=>!ids.includes(x));
save();renderCompras();
if(c.id)sbDelete('compras',c.id);
if(ids.length)sbParcelasApagarLote(ids);
toast('🗑️ Excluído!',false,'undoLast')}

// RENDER PARCELAS
function renderParcelas(){
const parc=gerarParcelas();const abertas=parc.filter(p=>p.status!=='pago');
const hojeStr=hojeISO();
const atrasadas=abertas.filter(p=>p.venc<hojeStr);
const futuras=abertas.filter(p=>p.venc>=hojeStr);
const totAtraso=atrasadas.reduce((a,p)=>a+p.valor,0);
const somaAte=d=>{const lim=maisDias(d);return futuras.filter(p=>p.venc<=lim).reduce((a,p)=>a+p.valor,0)};
document.getElementById('parcelasStats').innerHTML=`
<div class="stat ${atrasadas.length?'danger':''}"><div class="label">⚠️ Atrasadas</div><div class="value">${brl(totAtraso)}</div><div class="hint">${atrasadas.length} vencidas sem confirmação</div></div>
<div class="stat primary"><div class="label">⏰ Próx. 7 dias</div><div class="value">${brl(somaAte(7))}</div></div>
<div class="stat"><div class="label">📅 Próx. 30 dias</div><div class="value">${brl(somaAte(30))}</div></div>
<div class="stat"><div class="label">📆 Próx. 90 dias</div><div class="value">${brl(somaAte(90))}</div></div>`;
document.getElementById('parcCount').textContent=abertas.length+' em aberto'+(atrasadas.length?' · '+atrasadas.length+' atrasadas':'');

const porMes=somaPor(futuras,p=>p.venc.slice(0,7),p=>p.valor).sort((a,b)=>a.nome.localeCompare(b.nome));
const MN=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
document.getElementById('parcPorMes').innerHTML=porMes.length===0?'<p style="color:var(--text2);padding:8px 0">Nenhuma fatura futura 🎉</p>':porMes.map(m=>{const[y,mo]=m.nome.split('-');return`<div class="pmes-row"><span>${MN[parseInt(mo)-1]} De ${y}</span><b>${brl(m.total)}</b></div>`}).join('');

const linha=p=>`<div class="parc-item">
<div class="pi-main">
<div class="pi-title">${esc(p.desc)}</div>
<div class="pi-sub">${esc(p.forn||'—')} · parcela ${p.num}/${p.total} · vence ${dataBR(p.venc)}</div>
</div>
<span class="badge ${esc(p.status)}">${esc(p.status)}</span>
<div class="pi-valor">${brl(p.valor)}</div>
<button class="btn-pago" onclick="pagarParc('${esc(p.id)}')" title="Marcar como paga">✓ Pago</button>
</div>`;
const sep=(t,btn)=>`<div class="parc-sep"><span>${t}</span>${btn||''}</div>`;
let html='';
if(atrasadas.length)html+=sep('⚠️ Vencidas ('+atrasadas.length+')','<button class="btn btn-ghost" onclick="pagarTodasAtrasadas()">marcar todas como pagas</button>')+atrasadas.map(linha).join('');
if(futuras.length)html+=sep('⏳ A vencer ('+futuras.length+')')+futuras.map(linha).join('');
document.getElementById('parcelasList').innerHTML=abertas.length===0?'<p style="padding:16px 0;color:var(--text2)">Tudo quitado! 🎉</p>':html;
}
async function sbParcelaPaga(id){if(!SB){pendAdd('parcelas_pagas','parcela_id',id);return null}try{const{error}=await SB.from('parcelas_pagas').upsert({parcela_id:id},{onConflict:'parcela_id'});if(error)throw error;pendAddOk('parcelas_pagas','parcela_id',id);return true}catch(e){console.warn('Supabase parcela error:',e.message);pendAdd('parcelas_pagas','parcela_id',id);marcarSinc('err');return null}}
async function sbParcelaApagar(id){if(!SB){pendDel('parcelas_pagas','parcela_id',id);return null}try{const{error}=await SB.from('parcelas_pagas').delete().eq('parcela_id',id);if(error)throw error;pendOk('parcelas_pagas','parcela_id',id);return true}catch(e){console.warn('Supabase parcela delete:',e.message);pendDel('parcelas_pagas','parcela_id',id);marcarSinc('err');return null}}
let _lastParcPaga=null;
function pagarParc(id){if(S.parcelasPagas.includes(id))return;_lastParcPaga=id;S.parcelasPagas.push(id);sbParcelaPaga(id);save();renderParcelas();refreshObras();toast('✅ Parcela quitada!',false,'desfazerParcela')}
function desfazerParcela(){if(!_lastParcPaga)return;const id=_lastParcPaga;_lastParcPaga=null;S.parcelasPagas=S.parcelasPagas.filter(x=>x!==id);sbParcelaApagar(id);save();renderParcelas();refreshObras();toast('↩️ Parcela reaberta!')}
async function sbParcelasPagasLote(ids){if(!ids||!ids.length)return null;if(!SB){ids.forEach(x=>pendAdd('parcelas_pagas','parcela_id',x));return null}try{const{error}=await SB.from('parcelas_pagas').upsert(ids.map(x=>({parcela_id:x})),{onConflict:'parcela_id'});if(error)throw error;ids.forEach(x=>pendAddOk('parcelas_pagas','parcela_id',x));return true}catch(e){console.warn('Supabase lote pago:',e.message);ids.forEach(x=>pendAdd('parcelas_pagas','parcela_id',x));marcarSinc('err');return null}}
async function sbParcelasApagarLote(ids){if(!ids||!ids.length)return null;if(!SB){ids.forEach(x=>pendDel('parcelas_pagas','parcela_id',x));return null}try{const{error}=await SB.from('parcelas_pagas').delete().in('parcela_id',ids);if(error)throw error;ids.forEach(x=>pendOk('parcelas_pagas','parcela_id',x));return true}catch(e){console.warn('Supabase lote apagar:',e.message);ids.forEach(x=>pendDel('parcelas_pagas','parcela_id',x));marcarSinc('err');return null}}
let _lotePago=null;
function pagarTodasAtrasadas(){
const hojeStr=hojeISO();
const alvo=gerarParcelas().filter(p=>p.venc<hojeStr&&!S.parcelasPagas.includes(p.id));
if(!alvo.length)return;
const tot=alvo.reduce((a,p)=>a+p.valor,0);
if(!confirm('Marcar '+alvo.length+' parcelas vencidas como pagas?\n\nTotal: '+brl(tot)+'\n\nVocê poderá desfazer em seguida.'))return;
const ids=alvo.map(p=>p.id);
_lotePago=ids.slice();
ids.forEach(id=>{if(!S.parcelasPagas.includes(id))S.parcelasPagas.push(id)});
sbParcelasPagasLote(ids);save();renderParcelas();renderDash();refreshObras();
toast('✅ '+ids.length+' parcelas quitadas!',false,'desfazerLote')
}
function desfazerLote(){
if(!_lotePago)return;
const ids=_lotePago;_lotePago=null;
S.parcelasPagas=S.parcelasPagas.filter(x=>!ids.includes(x));
sbParcelasApagarLote(ids);save();renderParcelas();renderDash();refreshObras();
toast('↩️ '+ids.length+' parcelas reabertas')
}

// RENDER MÃO DE OBRA
function renderMO(){
const tot=S.maoDeObra.reduce((a,c)=>a+c.valor,0);
const _mo=obraAtual()||{};const _moArea=Number(_mo.area)||0;const _moVm2=Number(_mo.valorM2)||0;const ref=_moArea*_moVm2;
document.getElementById('moStats').innerHTML=`
<div class="stat ${ref&&tot>ref?'danger':''}"><div class="label">👷 Total pago</div><div class="value">${brlS(tot)}</div><div class="hint">${S.maoDeObra.length} pagamentos</div></div>
<div class="stat"><div class="label">📐 Referência (m²)</div><div class="value">${ref?brlS(ref):'—'}</div><div class="hint">${ref?_moArea+'m² × '+brl(_moVm2):'informe a área e o valor do m²'}</div></div>
<div class="stat ${ref&&tot>ref?'danger':''}"><div class="label">💵 Saldo</div><div class="value">${ref?brlS(ref-tot):'—'}</div><div class="hint">${ref?(tot>ref?'Acima da referência':'Dentro do orçamento'):'sem referência'}</div></div>`;

const porMes=somaPor(S.maoDeObra.filter(c=>c.data),c=>c.data.slice(0,7),c=>c.valor).sort((a,b)=>a.nome.localeCompare(b.nome));
const lbl=porMes.map(m=>{const[y,mo]=m.nome.split('-');return['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][parseInt(mo)-1]});
let cum=0;const acum=porMes.map(m=>{cum+=m.total;return cum});
mk('chartMo',{type:'bar',data:{labels:lbl,datasets:[{data:porMes.map(m=>m.total),backgroundColor:barGrad('#ef4444'),borderRadius:[6,6,0,0]}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brlS(v)}}}}});
mk('chartMoAcum',{type:'line',data:{labels:lbl,datasets:[{data:acum,borderColor:'#10b981',backgroundColor:'rgba(16,185,129,.1)',fill:true,tension:.4,pointBackgroundColor:'#10b981'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>brlS(v)}}}}});

document.getElementById('moBody').innerHTML=S.maoDeObra.slice().reverse().map((c,ri)=>{const i=S.maoDeObra.length-1-ri;return`<tr><td>${dataBR(c.data)}</td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor)}</td><td>${esc(c.descricao||'—')}</td><td><span class="badge ${esc(c.status)}">${esc(c.status)}</span></td><td><button class="btn btn-ghost btn-icon" onclick="editEntry('maoobra',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('maoDeObra',${i})">🗑️</button></td></tr>`}).join('');
document.getElementById('moCards').innerHTML=S.maoDeObra.slice().reverse().map((c,ri)=>{const i=S.maoDeObra.length-1-ri;return`<div class="mcard"><div class="mi"><div class="mt">${esc(c.descricao||'Pagamento')}</div><div class="ms">${dataBR(c.data)}</div></div><div class="mr"><div class="mv">${brl(c.valor)}</div><div class="ma"><span class="badge ${esc(c.status)}">${esc(c.status)}</span><button class="btn btn-ghost btn-icon" onclick="editEntry('maoobra',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('maoDeObra',${i})">🗑️</button></div></div></div>`}).join('');
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
document.getElementById('docBody').innerHTML=S.documentos.map((c,i)=>`<tr><td><b>${esc(c.servico)}</b></td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor)}</td><td>${dataBR(c.data)}</td><td>${esc(c.forma||'—')}</td><td><button class="btn btn-ghost btn-icon" onclick="editEntry('doc',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('documentos',${i})">🗑️</button></td></tr>`).join('');
document.getElementById('docCards').innerHTML=S.documentos.map((c,i)=>`<div class="mcard"><div class="mi"><div class="mt">${esc(c.servico)}</div><div class="ms">${dataBR(c.data)}${c.forma?' · '+esc(c.forma):''}</div></div><div class="mr"><div class="mv">${brl(c.valor)}</div><div class="ma"><button class="btn btn-ghost btn-icon" onclick="editEntry('doc',${i})">✏️</button><button class="btn btn-ghost btn-icon" onclick="delEntry('documentos',${i})">🗑️</button></div></div></div>`).join('');
}

// RENDER FIN (financiamento)
function renderFin(){
const juros=(S.juros||[]).slice().sort((a,b)=>String(a.data||'').localeCompare(String(b.data||''))),contas=S.contas||[];
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
document.getElementById('contasBody').innerHTML=contas.map((c,i)=>`<tr><td>${esc(c.item)}</td><td>${esc(c.mes||'—')}</td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor||0)}</td><td><span class="badge ${esc(c.status||'pago')}">${esc(c.status||'pago')}</span></td><td><button class="btn btn-ghost btn-icon" onclick="delEntry('contas',${i})">🗑️</button></td></tr>`).join('');
document.getElementById('contasCards').innerHTML=contas.map((c,i)=>`<div class="mcard"><div class="mi"><div class="mt">${esc(c.item)}</div><div class="ms">${esc(c.mes||'—')}</div></div><div class="mr"><div class="mv">${brl(c.valor||0)}</div><div class="ma"><span class="badge ${esc(c.status||'pago')}">${esc(c.status||'pago')}</span><button class="btn btn-ghost btn-icon" onclick="delEntry('contas',${i})">🗑️</button></div></div></div>`).join('');
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
const ter=rd['VALOR TERRENO']||0,escD=rd['DESPESAS ESCRITURA']||0,adi=rd['ADIANTAMENTO']||0;
const devido=rd['VALOR DEVIDO']||(ter-escD-adi);

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
<div class="jc-item neg"><span>(-) Metade das despesas de escritura</span><span class="jc-val">-${brl(escD)}</span></div>
<div class="jc-item neg"><span>(-) Adiantamento</span><span class="jc-val">-${brl(adi)}</span></div>
<div class="jc-total"><span>Valor devido</span><span class="jc-val">${brl(devido)}</span></div>`;

document.getElementById('despBox').innerHTML=rateio.map(c=>`
<div class="jc-row"><div class="jc-name">${esc(c.item||'—')}<span class="jc-date">${dataBR(c.data)}</span></div>
<div class="jc-valor">${brl(c.valor||0)}</div></div>`).join('')+`
<div class="jc-totrow"><span>Total</span><span class="jc-valor">${brl(totD)}</span></div>`;
}

// RENDER SPLIT (rateio Matheus)
function renderSplit(){
const rd=S.resumoDivisao||{};
const ter=rd['VALOR TERRENO']||0,escD=rd['DESPESAS ESCRITURA']||0,adi=rd['ADIANTAMENTO']||0,dev=rd['VALOR DEVIDO']||0,ret=rd['RETORNO']||0;
document.getElementById('splitBox').innerHTML=`<h3>🤝 Resumo do Rateio</h3>
<div class="split-item"><span>💰 Valor do Terreno</span><strong>${brl(ter)}</strong></div>
<div class="split-item"><span>📋 Despesas Escritura</span><strong>${brl(escD)}</strong></div>
<div class="split-item"><span>🤝 Adiantamento</span><strong>${brl(adi)}</strong></div>
<div class="split-item"><span>💵 Caio Deve</span><strong>${brl(dev)}</strong></div>
<div class="split-item"><span>🔄 Retorno Matheus</span><strong style="color:var(--green)">${brl(ret)}</strong></div>`;
mk('chartSplit',{type:'doughnut',data:{labels:['Terreno (metade)','Metade Escritura','Adiantamento'],datasets:[{data:[ter/2,escD/2,adi],backgroundColor:['#8b5cf6','#f59e0b','#10b981'],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}},cutout:'60%'}});
document.getElementById('splitBody').innerHTML=(S.rateio||[]).map(c=>`<tr><td>${esc(c.item||'—')}</td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor||0)}</td><td>${dataBR(c.data)}</td></tr>`).join('');
document.getElementById('splitCards').innerHTML=(S.rateio||[]).map(c=>`<div class="mcard"><div class="mi"><div class="mt">${esc(c.item||'—')}</div><div class="ms">${dataBR(c.data)}</div></div><div class="mr"><div class="mv">${brl(c.valor||0)}</div></div></div>`).join('');
}

// ============================================
// OBRAS — visao unificada de tudo
// ============================================
const CAT_OBRA=['Materiais','Mão de obra','Documentação e taxas','Financiamento','Contas de água e luz'];
const ORC_CATS=[{k:'materiais',nome:'Materiais de construção',cat:'Materiais'},
{k:'mao',nome:'Mão de obra',cat:'Mão de obra'},
{k:'doc',nome:'Documentação e taxas',cat:'Documentação e taxas'},
{k:'juros',nome:'Financiamento (juros)',cat:'Financiamento'},
{k:'contas',nome:'Contas de água e luz',cat:'Contas de água e luz'}];
const diasEntre=(a,b)=>Math.round((new Date(a+'T12:00:00')-new Date(b+'T12:00:00'))/864e5);

let _obraAba='resumo';
function obraTab(nome,btn){
_obraAba=nome;
document.querySelectorAll('.subtab').forEach(b=>b.classList.remove('active'));
if(btn)btn.classList.add('active');
document.querySelectorAll('.obra-pane').forEach(p=>p.classList.remove('active'));
const p=document.getElementById('obra-'+nome);if(p)p.classList.add('active');
renderObras();
}
function renderObras(){
const o=obraAtual();
const nomeEl=document.getElementById('obraNome');if(nomeEl)nomeEl.textContent=o?o.nome:'Obra';
renderObraSeletor();
const selo=document.getElementById('obraSelo');
if(selo){
if(!o)selo.style.display='none';
else if(o.id==='casa-caio'){selo.style.display=SB?'inline-block':'none';selo.textContent='☁️ sincronizada na nuvem'}
else{selo.style.display='inline-block';selo.textContent=SB_TEM_OBRAS?'☁️ sincronizada na nuvem':'📱 salva só neste aparelho';selo.title=SB_TEM_OBRAS?'Esta obra sincroniza entre aparelhos':'Para aparecer no celular, rode o arquivo supabase-obras.sql no Supabase'}
}
if(_obraAba==='resumo')renderObraResumo();
else if(_obraAba==='gastos')renderObraGastos();
else if(_obraAba==='orcamento')renderObraOrc();
else if(_obraAba==='parcelas')renderObraParc();
else if(_obraAba==='socio')renderObraSocio();
else if(_obraAba==='diario')renderDiario();
}

function renderObraSeletor(){
const sel=document.getElementById('obraSeletor');if(!sel)return;
sel.innerHTML=(S.obras||[]).map(o=>`<option value="${esc(o.id)}"${o.id===S.obraAtiva?' selected':''}>${esc(o.nome)}</option>`).join('');
}

function trocarObra(id){
if(!id||id===S.obraAtiva)return;
sincronizarAtiva();
S.obraAtiva=id;
aplicarObraAtiva();
save();
destroyAll();
renderObras();
toast('🏗️ '+obraAtual().nome);
if(id!=='casa-caio')puxarObraDaNuvem(id);
}

function openObraNova(){
modalType='obra';editIdx=null;editId=null;
document.getElementById('modalTitle').innerHTML='🏗️ Nova obra';
document.getElementById('modalBody').innerHTML=`
<div class="form-group"><label>Nome da obra</label><input id="o_nome" placeholder="Ex: Casa do Odair"></div>
<div class="form-group"><label>Local (cidade · UF)</label><input id="o_local" placeholder="Ex: Naviraí · MS"></div>
<div class="form-group"><label>Área construída (m²)</label><input id="o_area" type="number" step="0.1" min="0" placeholder="Ex: 60"></div>
<div class="form-group"><label>Valor do m² (opcional)</label><input id="o_vm2" type="number" step="0.01" min="0" placeholder="Ex: 1500"></div>
<p class="parc-sub" style="margin:10px 0 0">A obra nova começa vazia. Cada obra tem os seus próprios lançamentos, parcelas, orçamento e diário.</p>`;
document.getElementById('modal').classList.add('open');
}

function openObraEditar(){
const o=obraAtual();if(!o)return;
modalType='obra';editIdx=null;editId=o.id;
document.getElementById('modalTitle').innerHTML='✏️ Editar obra';
document.getElementById('modalBody').innerHTML=`
<div class="form-group"><label>Nome da obra</label><input id="o_nome" value="${esc(o.nome||'')}"></div>
<div class="form-group"><label>Local (cidade · UF)</label><input id="o_local" value="${esc(o.local||'')}"></div>
<div class="form-group"><label>Área construída (m²)</label><input id="o_area" type="number" step="0.1" min="0" value="${Number(o.area)||0}"></div>
<div class="form-group"><label>Valor do m² (opcional)</label><input id="o_vm2" type="number" step="0.01" min="0" value="${Number(o.valorM2)||0}"></div>`;
document.getElementById('modal').classList.add('open');
}

function excluirObra(){
const o=obraAtual();if(!o)return;
if((S.obras||[]).length<2)return toast('Você precisa ter pelo menos uma obra.',true);
if(!confirm('Excluir a obra "'+o.nome+'" e todos os dados dela?\n\nEssa ação não pode ser desfeita.'))return;
if(SB&&SB_TEM_OBRAS)SB.from('obras').delete().eq('id',o.id).then(()=>{}).catch(()=>{});
S.obras=S.obras.filter(x=>x.id!==o.id);
delete S.dados[o.id];
S.obraAtiva=S.obras[0].id;
aplicarObraAtiva();
save();destroyAll();renderObras();
toast('🗑️ Obra excluída');
}

// Junta compras, mao de obra, documentos, juros e contas numa lista so
function gastosUnificados(){
const out=[];
S.compras.forEach((c,i)=>out.push({tipo:'compra',i,item:c.material||'Compra',forn:c.fornecedor||'',data:c.data||'',valor:Number(c.valor)||0,cat:'Materiais',status:c.status==='pago'?'pago':'pendente',det:FORMAS[c.forma]||c.forma||''}));
S.maoDeObra.forEach((c,i)=>out.push({tipo:'maoobra',i,item:c.descricao?('Mão de obra · '+c.descricao):'Mão de obra',forn:'Equipe da obra',data:c.data||'',valor:Number(c.valor)||0,cat:'Mão de obra',status:c.status==='pago'?'pago':'pendente',det:''}));
S.documentos.forEach((c,i)=>out.push({tipo:'doc',i,item:c.servico||'Serviço',forn:c.forma||'',data:c.data||'',valor:Number(c.valor)||0,cat:'Documentação e taxas',status:'pago',det:''}));
(S.juros||[]).forEach((c,i)=>out.push({tipo:'juros',i,item:'Financiamento · juros',forn:'Banco',data:c.data||'',valor:Number(c.valor)||0,cat:'Financiamento',status:'pago',det:''}));
(S.contas||[]).forEach((c,i)=>out.push({tipo:'conta',i,item:c.item||'Conta',forn:'',data:'',valor:Number(c.valor)||0,cat:'Contas de água e luz',status:String(c.status||'pago').toLowerCase()==='pago'?'pago':'pendente',det:c.mes||''}));
return out;
}

function renderObraResumo(){
const g=gastosUnificados();
const total=g.reduce((a,x)=>a+x.valor,0);
const pago=g.filter(x=>x.status==='pago').reduce((a,x)=>a+x.valor,0);
const pend=total-pago;
const area=Number((obraAtual()||{}).area)||0;
document.getElementById('obraResumoSub').textContent=((obraAtual()||{}).local?obraAtual().local+' · ':'')+(area?area+' m² · ':'')+g.length+' lançamentos';
document.getElementById('obraStats').innerHTML=`
<div class="stat primary"><div class="label">💰 Total gasto</div><div class="value">${brl(total)}</div><div class="hint">${g.length} lançamentos</div></div>
<div class="stat"><div class="label">✅ Pago</div><div class="value" style="color:var(--green)">${brl(pago)}</div><div class="hint">${g.filter(x=>x.status==='pago').length} quitados</div></div>
<div class="stat ${pend>0?'danger':''}"><div class="label">⏳ Pendente</div><div class="value">${brl(pend)}</div><div class="hint">${g.filter(x=>x.status!=='pago').length} em aberto</div></div>
<div class="stat"><div class="label">📐 Custo por m²</div><div class="value">${area?brl(total/area):'—'}</div><div class="hint">${area?area+' m² construídos':'informe a área da obra'}</div></div>`;

const meses={};
for(const x of g){if(!x.data)continue;const m=x.data.slice(0,7);meses[m]=meses[m]||{t:0,p:0};meses[m].t+=x.valor;if(x.status==='pago')meses[m].p+=x.valor}
const ord=Object.keys(meses).sort();
const MN=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
const lbl=ord.map(m=>{const[y,mo]=m.split('-');return MN[parseInt(mo)-1]+'/'+y.slice(2)});
mk('chartObraMes',{type:'bar',data:{labels:lbl,datasets:[
{label:'Total',data:ord.map(m=>meses[m].t),backgroundColor:barGrad('#8b5cf6'),borderRadius:[6,6,0,0]},
{label:'Pago',data:ord.map(m=>meses[m].p),backgroundColor:barGrad('#10b981'),borderRadius:[6,6,0,0]}]},
options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'},tooltip:{callbacks:{label:c=>' '+c.dataset.label+': '+brl(c.parsed.y)}}},scales:{y:{ticks:{callback:v=>brlS(v)}}}}});

const cats={};for(const x of g)cats[x.cat]=(cats[x.cat]||0)+x.valor;
mk('chartObraCat',{type:'doughnut',data:{labels:Object.keys(cats),datasets:[{data:Object.values(cats),backgroundColor:['#8b5cf6','#ef4444','#3b82f6','#f59e0b','#10b981'],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'},tooltip:{callbacks:{label:c=>' '+brl(c.parsed)}}},cutout:'60%'}});

const f={};for(const x of g)f[x.forn||'Sem fornecedor']=(f[x.forn||'Sem fornecedor']||0)+x.valor;
const top=Object.entries(f).sort((a,b)=>b[1]-a[1]).slice(0,10);
mk('chartObraForn',{type:'bar',data:{labels:top.map(x=>x[0]),datasets:[{data:top.map(x=>x[1]),backgroundColor:barGrad('#f59e0b'),borderRadius:8}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' '+brl(c.parsed.x)}}},scales:{x:{ticks:{callback:v=>brlS(v)}}}}});
}

let _tGastos=null;
function buscaGastos(){clearTimeout(_tGastos);_tGastos=setTimeout(renderObraGastos,220)}
function acoesGasto(x){
const ed={compra:'compra',maoobra:'maoobra',doc:'doc'}[x.tipo];
const arr={compra:'compras',maoobra:'maoDeObra',doc:'documentos',juros:'juros',conta:'contas'}[x.tipo];
return (ed?`<button class="btn btn-ghost btn-icon" onclick="editEntry('${ed}',${x.i})" title="Editar">✏️</button>`:'')+
`<button class="btn btn-ghost btn-icon" onclick="delEntry('${arr}',${x.i})" title="Excluir">🗑️</button>`;
}
function renderObraGastos(){
const q=(document.getElementById('gq').value||'').toLowerCase();
const cat=document.getElementById('gcat').value;
const sit=document.getElementById('gsit').value;
let itens=gastosUnificados().filter(x=>(!q||x.item.toLowerCase().includes(q)||x.forn.toLowerCase().includes(q))&&(!cat||x.cat===cat)&&(!sit||x.status===sit));
itens.sort((a,b)=>String(b.data||'').localeCompare(String(a.data||'')));
const total=itens.reduce((a,x)=>a+x.valor,0);
const pago=itens.filter(x=>x.status==='pago').reduce((a,x)=>a+x.valor,0);
document.getElementById('gastosStats').innerHTML=`
<div class="stat primary"><div class="label">💰 Total filtrado</div><div class="value">${brl(total)}</div><div class="hint">${itens.length} lançamentos</div></div>
<div class="stat"><div class="label">✅ Pago</div><div class="value" style="color:var(--green)">${brl(pago)}</div></div>
<div class="stat ${total-pago>0?'danger':''}"><div class="label">⏳ Pendente</div><div class="value">${brl(total-pago)}</div></div>`;
document.getElementById('gastosBody').innerHTML=itens.length?itens.map(x=>`<tr>
<td><b>${esc(x.item)}</b>${x.det?' <span style="color:var(--text2)">· '+esc(x.det)+'</span>':''}<div style="font-size:11px;color:var(--text2);margin-top:2px">${esc(x.cat)}</div></td>
<td>${esc(x.forn||'—')}</td><td>${x.data?dataBR(x.data):'—'}</td>
<td style="font-weight:600;color:var(--accent2);white-space:nowrap">${brl(x.valor)}</td>
<td style="white-space:nowrap"><span class="badge ${esc(x.status)}">${esc(x.status)}</span></td>
<td><div class="gasto-acoes">${acoesGasto(x)}</div></td></tr>`).join(''):'<tr><td colspan="6" style="text-align:center;color:var(--text2);padding:28px">Nenhum lançamento com esses filtros</td></tr>';
document.getElementById('gastosCards').innerHTML=itens.map(x=>`<div class="mcard"><div class="mi"><div class="mt">${esc(x.item)}</div><div class="ms">${esc(x.cat)}${x.forn?' · '+esc(x.forn):''}${x.data?' · '+dataBR(x.data):''}</div></div><div class="mr"><div class="mv">${brl(x.valor)}</div><div class="ma"><span class="badge ${esc(x.status)}">${esc(x.status)}</span>${acoesGasto(x)}</div></div></div>`).join('');
}

function renderObraOrc(){
const g=gastosUnificados();const o=S.orcamento||{};
const cons={};for(const x of g)cons[x.cat]=(cons[x.cat]||0)+x.valor;
let totP=0,totC=0;
document.getElementById('orcList').innerHTML=ORC_CATS.map(c=>{
const prev=Number(o[c.k])||0,real=cons[c.cat]||0;totP+=prev;totC+=real;
const pct=prev>0?Math.min(100,real/prev*100):(real>0?100:0);
const over=prev>0&&real>prev;
const selo=prev>0?(over?'Acima do previsto':'Dentro do previsto'):'Sem previsão';
return `<div class="orc-card">
<div class="orc-top"><div class="orc-name">${c.nome}</div><span class="badge ${over?'atrasado':(prev>0?'pago':'cat')}" style="text-transform:none">${selo}</span></div>
<div class="prog"><div class="prog-fill ${over?'over':''}" style="width:${pct}%"></div></div>
<div class="orc-nums"><span>Consumido <b>${brl(real)}</b></span><span>${prev>0?(over?('Excedeu <b style="color:var(--red)">'+brl(real-prev)+'</b>'):('Restam <b>'+brl(prev-real)+'</b>')):''}</span></div>
<div class="orc-nums"><span>Previsto: ${prev>0?brl(prev):'não definido'}</span></div>
</div>`}).join('');
document.getElementById('orcSub').innerHTML=`Previsto <b>${brl(totP)}</b> · consumido <b>${brl(totC)}</b> · saldo <b style="color:${totP-totC<0?'var(--red)':'var(--green)'}">${brl(totP-totC)}</b>`;
}

function openOrcamento(){
modalType='orcamento';editIdx=null;editId=null;
const o=S.orcamento||{};
document.getElementById('modalTitle').innerHTML='✏️ Orçamento por etapa';
document.getElementById('modalBody').innerHTML=ORC_CATS.map(c=>`<div class="form-group"><label>${c.nome}</label><input id="o_${c.k}" type="number" step="0.01" min="0" value="${Number(o[c.k])||0}"></div>`).join('')+'<p class="parc-sub" style="margin:10px 0 0">Deixe 0 nas etapas que você não quer controlar.</p>';
document.getElementById('modal').classList.add('open');
}

function renderObraParc(){
const parc=gerarParcelas();const hoje=hojeISO();
const abertas=parc.filter(p=>p.status!=='pago');
const atras=abertas.filter(p=>p.venc<hoje);
const prox7=abertas.filter(p=>p.venc>=hoje&&p.venc<=maisDias(7));
const tot=a=>a.reduce((s,p)=>s+p.valor,0);
document.getElementById('obraParcStats').innerHTML=`
<div class="stat ${atras.length?'danger':''}"><div class="label">⚠️ Vencidas</div><div class="value">${brl(tot(atras))}</div><div class="hint">${atras.length} parcelas</div></div>
<div class="stat"><div class="label">⏰ Vencem em 7 dias</div><div class="value">${brl(tot(prox7))}</div><div class="hint">${prox7.length} parcelas</div></div>
<div class="stat primary"><div class="label">💳 A pagar no total</div><div class="value">${brl(tot(abertas))}</div><div class="hint">${abertas.length} parcelas</div></div>`;
document.getElementById('obraParcCount').textContent=abertas.length+' em aberto';
document.getElementById('obraParcList').innerHTML=abertas.length?abertas.map(p=>{
const aviso=p.status==='atrasado'?('vencida há '+diasEntre(hoje,p.venc)+' dias'):(p.venc===hoje?'vence hoje':'em dia');
return `<div class="parc-item"><div class="pi-main"><div class="pi-title">${esc(p.desc)}</div><div class="pi-sub">${esc(p.forn||'—')} · ${p.num}/${p.total} · ${dataBR(p.venc)} · ${aviso}</div></div><div class="pi-valor">${brl(p.valor)}</div><button class="btn-pago" onclick="pagarParc('${esc(p.id)}')" title="Marcar como paga">✓ Pago</button></div>`}).join(''):'<p style="padding:16px 0;color:var(--text2)">Tudo quitado! 🎉</p>';
}

function renderObraSocio(){
const rd=S.resumoDivisao||{},rateio=S.rateio||[];
const totD=rateio.reduce((a,c)=>a+(c.valor||0),0);
const ter=rd['VALOR TERRENO']||0,escD=rd['DESPESAS ESCRITURA']||0,adi=rd['ADIANTAMENTO']||0,dev=rd['VALOR DEVIDO']||0,ret=rd['RETORNO']||0;
document.getElementById('obraSocioStats').innerHTML=`
<div class="stat primary"><div class="label">🤝 Total dividido</div><div class="value">${brl(totD)}</div><div class="hint">${rateio.length} despesas</div></div>
<div class="stat"><div class="label">👤 Parte de Matheus (50%)</div><div class="value">${brl(totD/2)}</div></div>
<div class="stat"><div class="label">💰 Adiantamento</div><div class="value" style="color:var(--green)">${brl(adi)}</div></div>
<div class="stat danger"><div class="label">📌 Você deve a Matheus</div><div class="value">${brl(dev)}</div><div class="hint">retorno ${brl(ret)}</div></div>`;
document.getElementById('obraSocioBody').innerHTML=rateio.map(c=>`<tr><td>${esc(c.item||'—')}</td><td style="font-weight:600;color:var(--accent2)">${brl(c.valor||0)}</td><td>${dataBR(c.data)}</td></tr>`).join('');
document.getElementById('obraSocioCards').innerHTML=rateio.map(c=>`<div class="mcard"><div class="mi"><div class="mt">${esc(c.item||'—')}</div><div class="ms">${dataBR(c.data)}</div></div><div class="mr"><div class="mv">${brl(c.valor||0)}</div></div></div>`).join('');
}

function renderDiario(){
const d=(S.diario||[]).map((x,i)=>Object.assign({},x,{_i:i})).sort((a,b)=>String(b.data||'').localeCompare(String(a.data||'')));
document.getElementById('diarioList').innerHTML=d.length?d.map(x=>`<div class="diario-item"><div class="diario-data">${dataBR(x.data)}</div><div class="diario-titulo">${esc(x.titulo||'Registro')}</div><div class="diario-texto">${esc(x.texto||'')}</div><div style="margin-top:12px"><button class="btn btn-ghost btn-icon" onclick="delDiario(${x._i})" title="Excluir">🗑️</button></div></div>`).join(''):'<p class="parc-sub">Nenhum registro ainda. Use o botão acima para anotar o andamento da obra.</p>';
}
function openDiario(){
modalType='diario';editIdx=null;editId=null;
document.getElementById('modalTitle').innerHTML='📝 Novo registro no diário';
document.getElementById('modalBody').innerHTML=`
<div class="form-group"><label>Data</label><input id="d_data" type="date" value="${hojeISO()}"></div>
<div class="form-group"><label>Título</label><input id="d_titulo" placeholder="Ex: Laje concretada"></div>
<div class="form-group"><label>O que aconteceu</label><textarea id="d_texto" rows="4" style="width:100%;background:var(--card2);border:1px solid var(--border);border-radius:8px;padding:11px 14px;color:var(--text);font-size:14px;font-family:inherit;outline:none;resize:vertical"></textarea></div>`;
document.getElementById('modal').classList.add('open');
}
let _diarioApagado=null;
function delDiario(i){
const item=(S.diario||[])[i];if(!item)return;
_diarioApagado={idx:i,item:item};
S.diario.splice(i,1);save();renderDiario();
toast('🗑️ Registro excluído!',false,'undoDiario');
}
function undoDiario(){
if(!_diarioApagado)return;
S.diario=S.diario||[];
S.diario.splice(_diarioApagado.idx,0,_diarioApagado.item);
_diarioApagado=null;save();renderDiario();
toast('↩️ Registro restaurado!');
}

// MODAL
let modalType=null,editIdx=null,editId=null;
const MAP={compra:'compras',maoobra:'maoDeObra',doc:'documentos'};
function openModal(type,ref){
modalType=type;editIdx=(ref===undefined||ref===null)?null:Number(ref);
// Guarda o ID, nao a posicao: a lista pode ser reordenada por uma sincronizacao no meio da edicao
editId=editIdx===null?null:((((S[MAP[type]]||[])[editIdx])||{}).id||null);
const ed=editIdx!==null;
const m=document.getElementById('modal');const t=document.getElementById('modalTitle');const b=document.getElementById('modalBody');
if(type==='compra'){t.innerHTML=ed?'✏️ Editar compra':'🧱 Nova compra';b.innerHTML=`
<div class="form-group"><label>Material</label><input id="f_material" placeholder="Ex: Cimento CP-II"></div>
<div class="form-row"><div class="form-group"><label>Quantidade</label><input id="f_quantidade" placeholder="Ex: 10 sacos"></div>
<div class="form-group"><label>Valor (R$)</label><input id="f_valor" type="number" step="0.01"></div></div>
<div class="form-row"><div class="form-group"><label>Forma de pagamento</label><select id="f_forma">${Object.entries(FORMAS).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select></div>
<div class="form-group"><label>Nº Parcelas (se cartão)</label><input id="f_parcelas" type="number" value="1" min="1"></div></div>
<div class="form-row"><div class="form-group"><label>Fornecedor</label><input id="f_fornecedor" placeholder="Ex: Imperio Construções"></div>
<div class="form-group"><label>Data</label><input id="f_data" type="date" value="${hojeISO()}"></div></div>
<div class="form-row"><div class="form-group"><label>Etapa</label><select id="f_categoria">${CATEGORIAS.map(c=>`<option>${c}</option>`).join('')}</select></div>
<div class="form-group"><label>Status</label><select id="f_status"><option value="pago">Pago</option><option value="pendente">Pendente</option></select></div></div>`}
else if(type==='maoobra'){t.innerHTML=ed?'✏️ Editar pagamento':'👷 Novo pagamento';b.innerHTML=`
<div class="form-row"><div class="form-group"><label>Data</label><input id="f_data" type="date" value="${hojeISO()}"></div>
<div class="form-group"><label>Valor (R$)</label><input id="f_valor" type="number" step="0.01"></div></div>
<div class="form-group"><label>Descrição</label><input id="f_descricao" placeholder="Ex: ROGERIO, PINTURA..."></div>
<div class="form-group"><label>Status</label><select id="f_status"><option value="pago">Pago</option><option value="pendente">Pendente</option></select></div>`}
else if(type==='doc'){t.innerHTML=ed?'✏️ Editar serviço':'📋 Novo serviço';b.innerHTML=`
<div class="form-group"><label>Serviço</label><input id="f_servico" placeholder="Ex: ITBI, Alvará..."></div>
<div class="form-row"><div class="form-group"><label>Valor (R$)</label><input id="f_valor" type="number" step="0.01"></div>
<div class="form-group"><label>Data</label><input id="f_data" type="date" value="${hojeISO()}"></div></div>
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
function closeModal(){document.getElementById('modal').classList.remove('open');modalType=null;editIdx=null;editId=null}
function refreshPage(){let cur=((document.querySelector('.page.active')||{}).id||'').replace('page-','');
if(cur==='compras')renderCompras();else if(cur==='maoobra')renderMO();else if(cur==='documentos')renderDocs();else if(cur==='financiamento')renderFin();else if(cur==='dashboard')renderDash();else if(cur==='parcelas')renderParcelas();else if(cur==='juros')renderJuros();else if(cur==='divisao')renderSplit();else if(cur==='obras')renderObras()}
// Redesenha a aba Obras so quando ela esta visivel
function refreshObras(){const p=document.getElementById('page-obras');if(p&&p.classList.contains('active'))renderObras()}

function saveEntry(){
const g=id=>{const e=document.getElementById('f_'+id);return e?e.value.trim():''};
const v=id=>{const e=document.getElementById('f_'+id);return e?Number(e.value)||0:0};
try{
if(modalType==='obra'){
const campo=id=>{const e=document.getElementById(id);return e?e.value.trim():''};
const nome=campo('o_nome');
const local=campo('o_local');
const area=Number(campo('o_area'))||0;
const vm2=Number(campo('o_vm2'))||0;
if(!nome)return toast('Informe o nome da obra!',true);
if(editId){
const o=S.obras.find(x=>x.id===editId);
if(o){o.nome=nome;o.local=local;o.area=area;o.valorM2=vm2}
if(editId==='casa-caio'){S.obra.area=area||72;S.obra.valorM2=vm2||1800}
save();closeModal();renderObras();enviarObra(o);
toast('✅ Obra atualizada!');
}else{
const id=uid();
S.obras.push({id:id,nome:nome,local:local,area:area,valorM2:vm2});
S.dados[id]=PACOTE_VAZIO();
sincronizarAtiva();
S.obraAtiva=id;
aplicarObraAtiva();
save();closeModal();destroyAll();renderObras();enviarObra(obraAtual());
toast('🏗️ Obra criada!');
}
return;
}
if(modalType==='orcamento'){
const o={};ORC_CATS.forEach(c=>{const e=document.getElementById('o_'+c.k);o[c.k]=e?Math.max(0,Number(e.value)||0):0});
S.orcamento=o;save();closeModal();
if(document.getElementById('page-obras').classList.contains('active'))renderObraOrc();
toast('✅ Orçamento salvo!');return;
}
if(modalType==='diario'){
const tit=document.getElementById('d_titulo').value.trim();
const txt=document.getElementById('d_texto').value.trim();
if(!tit)return toast('Informe o título do registro!',true);
S.diario=S.diario||[];
S.diario.push({id:uid(),data:document.getElementById('d_data').value||hojeISO(),titulo:tit,texto:txt});
save();closeModal();renderDiario();toast('📝 Registro salvo!');return;
}
if(editIdx!==null){
const arr=MAP[modalType];
if(editId){const achou=S[arr].findIndex(x=>x&&x.id===editId);if(achou<0){closeModal();return toast('⚠️ Este registro não existe mais. Recarregue a página.',true)}editIdx=achou}
const it=S[arr][editIdx];if(!it){closeModal();return}
if(modalType==='compra'){const mat=g('material');if(!mat)return toast('Informe o material!',true);
Object.assign(it,{quantidade:g('quantidade'),material:mat,valor:v('valor'),forma:g('forma'),parcelas:Math.min(60,Math.max(1,Math.round(v('parcelas')||1))),fornecedor:g('fornecedor'),data:g('data'),status:g('status'),categoria:g('categoria')});
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
const item={id:uid(),quantidade:g('quantidade'),material:mat,valor:v('valor'),forma:g('forma'),parcelas:Math.min(60,Math.max(1,Math.round(v('parcelas')||1))),fornecedor:g('fornecedor'),data:g('data'),pagador:'CAIO',status:g('status'),categoria:g('categoria'),_new:true};
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
refreshObras();
toast('🗑️ Excluído!',false,'undoLast')}
function undoLast(){if(!_lastDeleted)return;const{arr,item,parcelas}=_lastDeleted;if(arr==='compras')S.compras.unshift(item);else S[arr].splice(_lastDeleted.idx,0,item);
if(parcelas&&parcelas.length){S.parcelasPagas=[...new Set([...(S.parcelasPagas||[]),...parcelas])];sbParcelasPagasLote(parcelas)}
_lastDeleted=null;save();
const sbTable={maoDeObra:'mao_de_obra',documentos:'documentos',juros:'juros',contas:'contas',compras:'compras'};
const t=sbTable[arr];if(t&&item&&item.id)sbPush(t,cloudRow(item));
const renders={maoDeObra:renderMO,documentos:renderDocs,juros:renderFin,contas:renderFin};(renders[arr]||renderCompras)();refreshObras();toast('↩️ Restaurado!')}

function resetAll(){localStorage.removeItem('obra-facil-v2');S=JSON.parse(JSON.stringify(SEED));if(!S.dados)S.dados={};if(!S.dados['casa-caio'])S.dados['casa-caio']=pacoteCasa();S.obraAtiva='casa-caio';aplicarObraAtiva();save();toast('🔄 Dados restaurados!');renderObras()}

// Offline: os dados continuam salvos no aparelho, só não sincroniza
if(typeof window!=='undefined'){
window.addEventListener('offline',()=>{marcarSinc('off');toast('📴 Sem internet — seus dados continuam salvos neste aparelho',true)});
window.addEventListener('online',()=>{toast('📶 Internet de volta! Sincronizando...');sbPullAll(false).then(()=>reenviarPendencias())});
if(navigator.onLine===false)marcarSinc('off');else if(!SB)marcarSinc('local');
// Duas abas/atalhos abertos: mantem os dois lados iguais
window.addEventListener('storage',e=>{
if(e.key!=='obra-facil-v2'||!e.newValue)return;
try{const d=JSON.parse(e.newValue);
if(d.compras)S.compras=d.compras;
if(d.maoDeObra)S.maoDeObra=d.maoDeObra;
if(d.documentos)S.documentos=d.documentos;
if(d.parcelasPagas)S.parcelasPagas=d.parcelasPagas;
if(d.juros)S.juros=d.juros;
if(d.contas)S.contas=d.contas;
refreshPage()}catch(err){}
});
// App instalavel + abre sem internet
if('serviceWorker' in navigator&&location.protocol==='https:'){
window.addEventListener('load',()=>{navigator.serviceWorker.register('/sw.js').catch(e=>console.warn('SW:',e.message))});
}
}

function exportCSV(){let csv='Categoria;Material;Valor;Forma;Data;Fornecedor;Status;Etapa\n';
S.compras.forEach(c=>{csv+=`Compra;${c.material};${c.valor};${c.forma}${c.parcelas>1?c.parcelas+'x':''};${c.data||''};${c.fornecedor||''};${c.status};${c.categoria}\n`});
S.maoDeObra.forEach(c=>{csv+=`MaoObra;;;${c.valor};;${c.data};${c.status};;${c.descricao||''}\n`});
S.documentos.forEach(c=>{csv+=`Doc;${c.servico};${c.valor};;${c.data||''};;;${c.forma||''}\n`});
const blob=new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='obra_casa_caio.csv';a.click();toast('📥 CSV exportado!')}

// ============================================
// STATUS DE SINCRONIZACAO + BACKUP
// ============================================
let _ultimaSinc=null;
function marcarSinc(estado){
const el=document.getElementById('syncChip');if(!el)return;
if(estado==='ok'){_ultimaSinc=new Date();el.className='sync-chip ok';el.textContent='☁️';el.title='Sincronizado às '+_ultimaSinc.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}
else if(estado==='off'){el.className='sync-chip off';el.textContent='📴';el.title='Sem internet — os dados estão salvos neste aparelho'}
else if(estado==='local'){el.className='sync-chip off';el.textContent='📴';el.title='Somente neste aparelho — a nuvem não está disponível'}
else{el.className='sync-chip err';el.textContent='⚠️';el.title='Falha ao sincronizar — os dados estão salvos neste aparelho'}
}
function baixarBackup(){
try{
sincronizarAtiva();
const dados={geradoEm:new Date().toISOString(),versao:3,obraAtiva:S.obraAtiva,obras:S.obras,dados:S.dados,obra:S.obra,orcamento:S.orcamento,diario:S.diario,compras:S.compras,maoDeObra:S.maoDeObra,documentos:S.documentos,parcelasPagas:S.parcelasPagas,juros:S.juros,contas:S.contas,rateio:S.rateio,resumoDivisao:S.resumoDivisao};
const blob=new Blob([JSON.stringify(dados,null,2)],{type:'application/json'});
const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='obra-facil-backup-'+hojeISO()+'.json';
document.body.appendChild(a);a.click();a.remove();
setTimeout(()=>URL.revokeObjectURL(a.href),3000);
toast('⬇️ Backup baixado! Guarde este arquivo.')}
catch(e){toast('Erro ao gerar backup: '+e.message,true)}}

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
