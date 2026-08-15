import sqlite3

conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()

cur.execute("SELECT id, name, slug FROM brands WHERE LOWER(name) LIKE '%gasgas%' OR LOWER(name) LIKE '%gas gas%'")
brands = cur.fetchall()
print("GASGAS Brands in DB:", brands)

if brands:
    brand_id = brands[0][0]
    cur.execute("SELECT id, name, category, thumbnail_url FROM motorcycles WHERE brand_id=? ORDER BY name", (brand_id,))
    models = cur.fetchall()
    print("\nGASGAS Models in DB:")
    for m in models:
        print(" ", m)

conn.close()
