"""Generates a synthetic procurement dataset in SQLite (procurement.db).
Synthetic data is used on purpose: it lets us plant known data-quality issues
(duplicates, missing values, migration mismatches) and verify SQL catches them."""
import sqlite3, random, os
random.seed(42)
if os.path.exists("procurement.db"): os.remove("procurement.db")
db = sqlite3.connect("procurement.db"); c = db.cursor()

c.executescript("""
CREATE TABLE suppliers_legacy(supplier_id INTEGER PRIMARY KEY, supplier_name TEXT, category TEXT, email TEXT, country TEXT, payment_terms TEXT);
CREATE TABLE suppliers_new(supplier_id INTEGER PRIMARY KEY, supplier_name TEXT, category TEXT, email TEXT, country TEXT, payment_terms TEXT);
CREATE TABLE purchase_orders(po_id INTEGER PRIMARY KEY, supplier_id INTEGER, po_date TEXT, po_amount REAL);
CREATE TABLE invoices(invoice_id INTEGER PRIMARY KEY, po_id INTEGER, invoice_date TEXT, invoice_amount REAL);
""")

cats = ["IT Services","Logistics","Office Supplies","Raw Materials","Facilities","Marketing"]
countries = ["India","USA","Germany","UK","Singapore"]
terms = ["Net 30","Net 45","Net 60"]
base = ["Apex","Nova","Bluewave","Sterling","Orion","Zenith","Vertex","Pioneer","Summit","Crest"]
suffix = ["Solutions","Traders","Logistics","Systems","Industries","Enterprises","Supplies","Group"]

names, seen = [], set()
while len(names) < 200:
    n = f"{random.choice(base)} {random.choice(suffix)} {random.randint(1,40)}"
    if n not in seen: seen.add(n); names.append(n)

rows = []
for i, n in enumerate(names, start=1):
    email = f"contact@{n.lower().replace(' ','')}.com"
    rows.append([i, n, random.choice(cats), email, random.choice(countries), random.choice(terms)])

# Planted issue 1: 12 duplicate suppliers (same name, new id)
nxt = 201
for r in random.sample(rows, 12):
    rows.append([nxt, r[1], r[2], r[3], r[4], r[5]]); nxt += 1
# Planted issue 2: missing values in legacy
for r in random.sample(rows, 10): r[3] = None          # missing email
for r in random.sample(rows, 8):  r[5] = None          # missing payment terms
c.executemany("INSERT INTO suppliers_legacy VALUES(?,?,?,?,?,?)", rows)

# Migration to new system with planted defects
new_rows = [r[:] for r in rows]
dropped = random.sample(new_rows, 7)                    # 7 records not migrated
new_rows = [r for r in new_rows if r not in dropped]
for r in random.sample(new_rows, 9): r[4] = random.choice(countries + ["USA "])   # country changed / trailing space
for r in random.sample(new_rows, 6): r[5] = "Net 30"                              # payment terms changed
c.executemany("INSERT INTO suppliers_new VALUES(?,?,?,?,?,?)", new_rows)

# Purchase orders and invoices
sup_ids = [r[0] for r in rows]
po_rows, inv_rows, inv_id = [], [], 1
for po in range(1, 1501):
    s = random.choice(sup_ids)
    d = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    amt = round(random.uniform(500, 50000), 2)
    po_rows.append((po, s, d, amt))
    if random.random() < 0.9:                           # ~10% POs not invoiced
        inv_amt = amt if random.random() < 0.93 else round(amt * random.uniform(0.9, 1.1), 2)
        inv_rows.append((inv_id, po, d, inv_amt)); inv_id += 1
c.executemany("INSERT INTO purchase_orders VALUES(?,?,?,?)", po_rows)
c.executemany("INSERT INTO invoices VALUES(?,?,?,?)", inv_rows)
db.commit(); db.close()
print("procurement.db created")
