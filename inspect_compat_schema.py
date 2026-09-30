import sqlite3

conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(modification_compatibility)")
cols = cur.fetchall()
print("Columns in modification_compatibility:")
for c in cols:
    print(" ", c[1], "(", c[2], ")")

conn.close()
