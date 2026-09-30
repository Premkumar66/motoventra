import sqlite3

conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(modifications)")
cols = cur.fetchall()
print("NOT NULL Columns in modifications:")
for c in cols:
    cid, name, type_, notnull, dflt_value, pk = c
    if notnull:
        print(f"  {name:30} ({type_}) | Default: {dflt_value}")

conn.close()
