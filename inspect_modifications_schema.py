import sqlite3

conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(modifications)")
cols = cur.fetchall()
print("Modifications Table Columns:")
for c in cols:
    print(" ", c[1], "(", c[2], ")")

conn.close()
