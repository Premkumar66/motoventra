import sqlite3
import os
import requests

DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
BACKEND_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend"
BASE_URL = "http://localhost:8000"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("===========================================================================")
print("CORRECTED AUDIT OF ALL MOTORCYCLE MODELS AND IMAGES")
print("===========================================================================")

cur.execute("""
SELECT br.name as brand_name, br.slug as brand_slug, m.id as model_id, m.name as model_name, m.category, m.thumbnail_url 
FROM motorcycles m
JOIN brands br ON m.brand_id = br.id
ORDER BY br.name, m.name
""")
rows = cur.fetchall()

total_models = len(rows)
missing_in_db = []
file_not_found = []
http_failed = []
ok_count = 0

for brand_name, brand_slug, model_id, model_name, category, thumb_url in rows:
    if not thumb_url:
        missing_in_db.append((brand_name, model_name, category))
        continue
    
    # Correct path resolution: thumb_url is '/static/images/...' -> app/static/images/...
    # backend directory is motomod-ai/backend/app
    app_relative = thumb_url.lstrip('/') # 'static/images/...'
    abs_path = os.path.join(BACKEND_DIR, "app", app_relative.replace('/', os.sep))
    
    if not os.path.exists(abs_path):
        file_not_found.append((brand_name, model_name, thumb_url, abs_path))
        continue

    # Test HTTP server response
    try:
        r = requests.head(BASE_URL + thumb_url, timeout=3)
        if r.status_code != 200:
            http_failed.append((brand_name, model_name, thumb_url, r.status_code))
        else:
            ok_count += 1
    except Exception as e:
        http_failed.append((brand_name, model_name, thumb_url, str(e)))

conn.close()

print(f"\nAudit Summary:")
print(f"  Total Models in DB: {total_models}")
print(f"  OK (Valid Image File & Serving HTTP 200): {ok_count}")
print(f"  Missing thumbnail_url in DB: {len(missing_in_db)}")
print(f"  File Missing on Disk: {len(file_not_found)}")
print(f"  HTTP Server Error: {len(http_failed)}")

if missing_in_db:
    print(f"\n--- {len(missing_in_db)} Models Missing thumbnail_url in DB ---")
    by_brand = {}
    for b, m, cat in missing_in_db:
        by_brand.setdefault(b, []).append((m, cat))
    for b, list_m in sorted(by_brand.items()):
        print(f"  Brand: {b} ({len(list_m)} models without DB thumbnail_url)")
        for m, cat in list_m[:5]:
            print(f"    - {m} [{cat}]")
        if len(list_m) > 5:
            print(f"    ... and {len(list_m) - 5} more")

if file_not_found:
    print(f"\n--- {len(file_not_found)} Models with Missing Files on Disk ---")
    for b, m, url, path in file_not_found:
        print(f"  [{b}] {m} -> {url}")

if http_failed:
    print(f"\n--- {len(http_failed)} Models with HTTP Server Errors ---")
    for b, m, url, err in http_failed:
        print(f"  [{b}] {m} -> {url} (Error: {err})")
