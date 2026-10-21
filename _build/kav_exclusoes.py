import os, re, glob, datetime

RAIZES = [r"C:\ProgramData\Kaspersky Lab", r"C:\Users\Odair\AppData\Local\KasperskyLab",
          r"C:\Users\Odair\AppData\Roaming\KasperskyLab"]

IGNORAR = ("detects.db", "reports.db", "traffic_stats.db", "ac_file_registry.kvs")
LIMITE = datetime.datetime.now() - datetime.timedelta(days=1)

achados = []
for raiz in RAIZES:
    if not os.path.isdir(raiz):
        continue
    for dirpath, dirnames, filenames in os.walk(raiz):
        for fn in filenames:
            if any(fn.startswith(i) for i in IGNORAR):
                continue
            p = os.path.join(dirpath, fn)
            try:
                st = os.stat(p)
                if datetime.datetime.fromtimestamp(st.st_mtime) < LIMITE or st.st_size > 8_000_000:
                    continue
                with open(p, "rb") as f:
                    b = f.read()
            except Exception:
                continue
            if b"opencode" in b:
                idx = [m.start() for m in re.finditer(rb"opencode", b)]
                achados.append((p, st.st_size, len(idx), b))

print("Arquivos de configuracao do Kaspersky com 'opencode' (ultimas 24h):")
if not achados:
    print("  NENHUM  -> as exclusoes provavelmente NAO foram adicionadas ainda")
for p, tam, n, b in achados[:12]:
    print(f"\n  {p}  ({tam} bytes, {n} ocorrencias)")
    for off in [m.start() for m in re.finditer(rb"opencode", b)][:4]:
        ini = max(0, off - 130)
        trecho = b[ini:off + 90]
        print("     ...", trecho.decode("latin-1", "replace").replace("\x00", "").strip()[:230])
