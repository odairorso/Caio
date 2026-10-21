import sqlite3, os, datetime, shutil

SRC = r"C:\ProgramData\Kaspersky Lab\AVP21.26\Data\detects.db"
DST = os.path.join(os.environ["TEMP"], "kav2.db")

def copia(src, dst):
    fs = open(src, "rb")
    with open(dst, "wb") as o:
        while True:
            b = fs.read(65536)
            if not b:
                break
            o.write(b)
    fs.close()

# copia com compartilhamento
import io
h = None
for modo in ("rb",):
    try:
        f = open(SRC, modo)
        with open(DST, "wb") as o:
            o.write(f.read())
        f.close()
    except Exception as e:
        print("aviso copia:", e)

def ft(ts):
    try:
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=int(ts) / 10)
    except Exception:
        return None

con = sqlite3.connect(DST)
con.row_factory = sqlite3.Row
verd = {r["Id"]: r["Name"] for r in con.execute("select Id,Name from verdicts")}
objs = {r["Id"]: r["Name"] for r in con.execute("select Id,Name from objects")}

print("TODAS AS DETECCOES REGISTRADAS")
print("-" * 76)
for t in con.execute("select * from threats order by Id"):
    quando = ft(t["UpdateTime"])
    nome = verd.get(t["VerdictId"], "(sem veredicto)")
    obj = objs.get(t["ObjectInfoId"], "?")
    print(f"  {quando}  | {nome}")
    print(f"      {obj}")

LIMITE = datetime.datetime(2026, 10, 21, 16, 30)
novas = [t for t in con.execute("select * from threats")
         if ft(t["UpdateTime"]) and ft(t["UpdateTime"]) > LIMITE]
print()
print(f"Novas deteccoes depois das 16:30 de hoje: {len(novas)}")
con.close()
