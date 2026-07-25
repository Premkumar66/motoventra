import sqlite3

conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()

cur.execute("SELECT id, name, slug, country FROM brands WHERE LOWER(name) LIKE '%beta%'")
brands = cur.fetchall()
print("Beta Brands:", brands)

if brands:
    brand_id = brands[0][0]
    cur.execute("SELECT id, name, category, thumbnail_url FROM motorcycles WHERE brand_id=?", (brand_id,))
    models = cur.fetchall()
    print("Beta Models:", models)

conn.close()
