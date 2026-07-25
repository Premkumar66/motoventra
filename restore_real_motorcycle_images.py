import sqlite3
import os
import re

DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"
STATIC_IMG_DIR = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images"

# High resolution real bike photos map
REAL_PHOTO_MAPPINGS = {
    # Bajaj Models
    "Avenger Cruise 220": "/static/images/bajaj_avenger_cruise_220.png",
    "CT 125X": "/static/images/bajaj_ct_125x.png",
    "Chetak Premium EV": "/static/images/bajaj_chetak_premium_ev.png",
    "Dominar 250": "/static/images/bajaj_dominar_250.png",
    "Dominar 400": "/static/images/bajaj_dominar_400.png",
    "Freedom 125 CNG": "/static/images/bajaj_freedom_125_cng.png",
    "Pulsar 220F": "/static/images/bajaj_pulsar_220f.png",
    "Pulsar N160": "/static/images/bajaj_pulsar_n160.png",
    "Pulsar N250": "/static/images/bajaj_pulsar_n250.png",
    "Pulsar NS125": "/static/images/bajaj_pulsar_ns125.png",
    "Pulsar NS160": "/static/images/bajaj_pulsar_ns160.png",
    "Pulsar NS200": "/static/images/bajaj_pulsar_ns200.png",

    # Benelli Models
    "502C Cruiser": "/static/images/benelli_502c_cruiser.png",
    "Imperiale 400": "/static/images/benelli_imperiale_400.png",
    "Leoncino 500": "/static/images/benelli_leoncino_500.png",
    "TNT 600i Inline 4": "/static/images/benelli_tnt_600i_inline_4.png",
    "TRK 502X": "/static/images/benelli_trk_502x.png",

    # BMW Models
    "CE02 eParkourer": "/static/images/bmw_ce02_eparkourer.png",
    "CE04 Electric": "/static/images/bmw_ce04_electric.png",
    "F900R": "/static/images/bmw_f900r.png",
    "F900XR": "/static/images/bmw_f900xr.png",
    "G310GS": "/static/images/bmw_g310gs.png",
    "G310R": "/static/images/bmw_g310r.png",
    "M1000RR": "/static/images/bmw_m1000rr.png",
    "R1250GS Adventure": "/static/images/bmw_r1250gs_adventure.png",
    "R1300GS": "/static/images/bmw_r1300gs.png",
    "R18 Cruiser": "/static/images/bmw_r18_cruiser.png",
    "S1000RR": "/static/images/bmw_s1000rr.png",
    "S1000XR": "/static/images/bmw_s1000xr.png",

    # Beta Models
    "EVO 300 Trial": "/static/images/beta_evo_300_trial.png",
    "RR 390 4T": "/static/images/beta_rr_390_4t.png",
    "Xtrainer 300 Enduro": "/static/images/beta_xtrainer_300_enduro.png",

    # Aprilia Models
    "RS 457": "/static/images/aprilia_rs_457.png",
    "RS 660": "/static/images/aprilia_rs_660.png",
    "RSV4 Factory 1100": "/static/images/aprilia_rsv4_factory_1100.png",
    "SR 160 Storm": "/static/images/aprilia_sr_160_storm.png",
    "SXR 160 Maxi": "/static/images/aprilia_sxr_160_maxi.png",
    "Tuareg 660 Rally": "/static/images/aprilia_tuareg_660_rally.png",
    "Tuono 660": "/static/images/aprilia_tuono_660.png",
    "Tuono V4 Factory": "/static/images/aprilia_tuono_v4_factory.png",

    # Ather Models
    "450S EV": "/static/images/ather_450s_ev.png",
    "450X Apex EV": "/static/images/ather_450x_apex_ev.png",
    "Rizta Z EV": "/static/images/ather_rizta_z_ev.png",

    # Royal Enfield Models
    "Classic 350": "/static/images/re_classic_350_bike.png",
    "Himalayan 450": "/static/images/re_himalayan_450_bike.png",
    "Hunter 350": "/static/images/re_hunter_350_bike.png",
    "Continental GT 650": "/static/images/re_gt_650_bike.png",

    # KTM Models
    "Duke 125": "/static/images/ktm_duke_125_bike.png",
    "Duke 200": "/static/images/ktm_duke_200_bike.png",
    "Duke 250": "/static/images/ktm_duke_250_bike.png",
    "Duke 390": "/static/images/ktm_duke_390.png",
    "RC 390": "/static/images/ktm_rc_390_bike.png",

    # Honda Models
    "CB350 H'ness": "/static/images/honda_cb350_hness_bike.png",
    "CBR650R": "/static/images/honda_cbr_650r.png",

    # Yamaha Models
    "MT-15 V2": "/static/images/yamaha_mt_15_bike.png",
    "YZF R15 V4": "/static/images/yamaha_r15_bike.png",

    # Suzuki Models
    "Hayabusa": "/static/images/suzuki_hayabusa_bike.png",

    # TVS Models
    "Apache RR 310": "/static/images/tvs_apache_bike.png"
}

def clean_and_restore():
    print("===========================================================================")
    print("RESTORING AUTHENTIC MOTORCYCLE IMAGES IN DATABASE & CLEANING SYNTHETICS")
    print("===========================================================================")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Step 1: Remove synthetic card images that were generated
    removed_files = 0
    for f in os.listdir(STATIC_IMG_DIR):
        # Remove placeholder synthetic card images generated earlier
        if any(prefix in f for prefix in ['_motorrad_', 'harley_davidson_', 'ola_electric_', 'matter_', 'revolt_', 'ultraviolette_']) and f.endswith('.png'):
            fp = os.path.join(STATIC_IMG_DIR, f)
            try:
                os.remove(fp)
                removed_files += 1
            except Exception as e:
                pass

    print(f"Removed {removed_files} synthetic placeholder files.")

    # Step 2: Set thumbnail_url to NULL for general models so fallback getBikeImg() works,
    # and set EXACT REAL PHOTO URL for all authentic models!
    cur.execute("UPDATE motorcycles SET thumbnail_url=NULL")
    print("Reset all motorcycle thumbnail_urls to NULL.")

    updated_real = 0
    for model_name, photo_url in REAL_PHOTO_MAPPINGS.items():
        # Check if file exists
        fn = photo_url.split('/')[-1]
        fp = os.path.join(STATIC_IMG_DIR, fn)
        if os.path.exists(fp) and os.path.getsize(fp) > 20000:
            cur.execute("UPDATE motorcycles SET thumbnail_url=?, updated_at=CURRENT_TIMESTAMP WHERE name=?", (photo_url, model_name))
            if cur.rowcount > 0:
                updated_real += cur.rowcount
                print(f"  [REAL PHOTO MATCHED] {model_name:25} -> {photo_url} ({os.path.getsize(fp)//1024} KB)")

    conn.commit()

    # Verify counts
    cur.execute("SELECT COUNT(*) FROM motorcycles WHERE thumbnail_url IS NOT NULL")
    has_photo = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM motorcycles")
    total = cur.fetchone()[0]

    conn.close()

    print(f"\nCompletion Summary:")
    print(f"  Total Models in DB: {total}")
    print(f"  Models with Authentic Real Photos: {has_photo}")
    print(f"  Models with Smart Fallbacks: {total - has_photo}")

if __name__ == "__main__":
    clean_and_restore()
