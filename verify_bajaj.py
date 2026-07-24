import requests

BASE = 'http://localhost:8000'
BAJAJ_IMAGES = [
    ('Avenger Cruise 220', '/static/images/bajaj_avenger_cruise_220.png'),
    ('CT 125X',            '/static/images/bajaj_ct_125x.png'),
    ('Chetak Premium EV',  '/static/images/bajaj_chetak_premium_ev.png'),
    ('Dominar 250',        '/static/images/bajaj_dominar_250.png'),
    ('Dominar 400',        '/static/images/bajaj_dominar_400.png'),
    ('Freedom 125 CNG',    '/static/images/bajaj_freedom_125_cng.png'),
    ('Pulsar 220F',        '/static/images/bajaj_pulsar_220f.png'),
    ('Pulsar N160',        '/static/images/bajaj_pulsar_n160.png'),
    ('Pulsar N250',        '/static/images/bajaj_pulsar_n250.png'),
    ('Pulsar NS125',       '/static/images/bajaj_pulsar_ns125.png'),
    ('Pulsar NS160',       '/static/images/bajaj_pulsar_ns160.png'),
    ('Pulsar NS200',       '/static/images/bajaj_pulsar_ns200.png'),
]

print("=== BAJAJ MODEL IMAGE VERIFICATION ===")
ok = fail = 0
for name, path in BAJAJ_IMAGES:
    r = requests.head(BASE + path, timeout=5)
    size_kb = int(r.headers.get('content-length', 0)) // 1024
    status = 'OK' if r.status_code == 200 else f'FAIL({r.status_code})'
    source = 'REAL' if size_kb > 500 else 'SMALL'
    print(f"  [{status}] {name:25} {size_kb:5} KB  [{source}]  {path.split('/')[-1]}")
    if r.status_code == 200: ok += 1
    else: fail += 1

print(f"\nTotal: {ok} OK, {fail} FAILED")

# Also verify DB has correct thumbnail_url
import sqlite3
conn = sqlite3.connect('motomod-ai/backend/motomod_ai.db')
cur = conn.cursor()
cur.execute("SELECT name, thumbnail_url FROM motorcycles WHERE thumbnail_url LIKE '%bajaj%' ORDER BY name")
print("\n=== DB thumbnail_url for Bajaj models ===")
for r in cur.fetchall():
    print(f"  {r[0]:25} -> {r[1]}")
conn.close()
