import sqlite3

DB_PATH = 'motomod-ai/backend/motomod_ai.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
SELECT m.id, m.name, m.category, m.thumbnail_url, br.name 
FROM motorcycles m 
JOIN brands br ON m.brand_id=br.id 
WHERE m.name IN ('F900R', 'F900XR', 'G310GS', 'G310R')
""")
rows = cur.fetchall()
print("=== 4 BMW Models DB Status ===")
for r in rows:
    print(r)

conn.close()
