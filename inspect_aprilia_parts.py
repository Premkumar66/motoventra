import sqlite3

conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()

print("=== 1. Checking Aprilia Brand & Models in DB ===")
cur.execute("SELECT id, name FROM brands WHERE LOWER(name) LIKE '%aprilia%'")
brand = cur.fetchone()
print("Brand:", brand)

if brand:
    brand_id = brand[0]
    cur.execute("SELECT id, name, category FROM motorcycles WHERE brand_id=? ORDER BY name", (brand_id,))
    motos = cur.fetchall()
    print(f"\nFound {len(motos)} Aprilia Motorcycles:")
    moto_ids = []
    for m in motos:
        print(f"  Moto ID: {m[0]} | {m[1]:25} | Category: {m[2]}")
        moto_ids.append(m[0])
        
    cur.execute(f"SELECT id, motorcycle_id, variant_name, year FROM motorcycle_variants WHERE motorcycle_id IN ({','.join(['?']*len(moto_ids))})", moto_ids)
    variants = cur.fetchall()
    print(f"\nFound {len(variants)} Aprilia Variants:")
    variant_ids = []
    for v in variants:
        print(f"  Variant ID: {v[0]} | {v[2]:30} | Year: {v[3]}")
        variant_ids.append(v[0])

    print("\n=== 2. Checking Existing Modification Mappings ===")
    if variant_ids:
        cur.execute(f"SELECT count(*) FROM modification_compatibility WHERE variant_id IN ({','.join(['?']*len(variant_ids))})", variant_ids)
        compat_count = cur.fetchone()[0]
        print(f"Total compatibility records for Aprilia variants: {compat_count}")

print("\n=== 3. Checking Modification Categories ===")
cur.execute("SELECT id, name, slug FROM modification_categories ORDER BY name")
cats = cur.fetchall()
for c in cats:
    print(f"  Cat ID: {c[0]} | {c[1]:30} | slug: {c[2]}")

conn.close()
