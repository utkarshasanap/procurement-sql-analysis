import sqlite3
db = sqlite3.connect("procurement.db")
blocks = [b.strip() for b in open("queries.sql").read().split(";") if b.strip()]
out = []
for b in blocks:
    title = b.splitlines()[0]
    cur = db.execute(b); cols = [d[0] for d in cur.description]
    out.append(f"{title}\n{cols}")
    out += [str(r) for r in cur.fetchall()]; out.append("")
open("results.txt","w").write("\n".join(out)); print("\n".join(out))
