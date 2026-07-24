import sqlite3
conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()
cur.execute("SELECT brand_id, name, thumbnail_url FROM motorcycles WHERE thumbnail_url IS NOT NULL LIMIT 10")
for r in cur.fetchall():
    print(r)
conn.close()
