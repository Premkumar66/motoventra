import requests

test_images = [
    '/static/images/benelli_502c_cruiser.png',
    '/static/images/benelli_imperiale_400.png',
    '/static/images/benelli_leoncino_500.png',
    '/static/images/benelli_tnt_600i_inline_4.png',
    '/static/images/benelli_trk_502x.png',
    '/static/images/bajaj_avenger_cruise_220.png',
    '/static/images/bajaj_ct_125x.png',
    '/static/images/bajaj_chetak_premium_ev.png',
    '/static/images/bajaj_dominar_250.png',
    '/static/images/bajaj_dominar_400.png',
    '/static/images/bajaj_freedom_125_cng.png',
    '/static/images/bajaj_pulsar_220f.png',
    '/static/images/bajaj_pulsar_n160.png',
    '/static/images/bajaj_pulsar_n250.png',
    '/static/images/bajaj_pulsar_ns125.png',
    '/static/images/bajaj_pulsar_ns160.png',
    '/static/images/bajaj_pulsar_ns200.png',
    '/static/images/ather_450s_ev.png',
    '/static/images/ather_450x_apex_ev.png',
    '/static/images/ather_rizta_z_ev.png',
]

base = 'http://localhost:8000'
ok = 0
fail = 0
for path in test_images:
    r = requests.head(base + path)
    status = 'OK' if r.status_code == 200 else f'FAIL ({r.status_code})'
    size = r.headers.get('content-length', '?')
    print(f"{status} | {size} bytes | {path.split('/')[-1]}")
    if r.status_code == 200:
        ok += 1
    else:
        fail += 1

print(f"\nTotal: {ok} OK, {fail} FAILED")
