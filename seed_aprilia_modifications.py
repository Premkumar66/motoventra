import sqlite3
import uuid

DB_PATH = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\motomod_ai.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== Fetching Aprilia Variant IDs ===")
cur.execute("""
    SELECT v.id, m.name 
    FROM motorcycle_variants v 
    JOIN motorcycles m ON v.motorcycle_id = m.id 
    JOIN brands b ON m.brand_id = b.id 
    WHERE LOWER(b.name) LIKE '%aprilia%'
""")
variant_rows = cur.fetchall()

variant_map = {}
for vid, mname in variant_rows:
    variant_map[mname] = vid
    print(f"  Mapped {mname:22} -> Variant ID: {vid}")

# Fetch category map by slug
cur.execute("SELECT id, slug FROM modification_categories")
cat_rows = cur.fetchall()
cat_map = {slug: cid for cid, slug in cat_rows}

# Define rich Aprilia modifications
APRILIA_MODIFICATIONS = [
    # 1. Exhaust Systems
    {
        "name": "Akrapovič Racing Line Slip-On Exhaust (Titanium)",
        "brand": "Akrapovič",
        "cat": "exhaust-systems",
        "desc": "Ultra-lightweight titanium slip-on silencer with carbon fiber end cap. Delivers race-bred sound and power gains.",
        "price_inr": 85000,
        "hp_change": 4.5,
        "torque_change": 3.2,
        "weight_change": -3.1,
        "mileage_change": -0.5,
        "material": "Titanium & Carbon",
        "compatible_models": ["RS 457", "RS 660", "Tuono 660"]
    },
    {
        "name": "SC-Project CRT Full Titanium Exhaust System",
        "brand": "SC-Project",
        "cat": "exhaust-systems",
        "desc": "MotoGP derived full titanium racing system with high-pitch exhaust note and maximum peak horsepower delivery.",
        "price_inr": 145000,
        "hp_change": 8.2,
        "torque_change": 5.4,
        "weight_change": -5.2,
        "mileage_change": -1.0,
        "material": "Full Titanium",
        "compatible_models": ["RSV4 Factory 1100", "Tuono V4 Factory"]
    },
    {
        "name": "Arrow Pro-Race Slip-On Exhaust",
        "brand": "Arrow",
        "cat": "exhaust-systems",
        "desc": "Nichrom stainless steel silencer designed for adventure and sport riding with removable DB killer.",
        "price_inr": 48000,
        "hp_change": 3.1,
        "torque_change": 2.8,
        "weight_change": -2.4,
        "mileage_change": -0.2,
        "material": "Nichrom Stainless Steel",
        "compatible_models": ["Tuareg 660 Rally", "RS 660", "Tuono 660"]
    },
    {
        "name": "LeoVince LV ONE EVO Stainless Steel Exhaust",
        "brand": "LeoVince",
        "cat": "exhaust-systems",
        "desc": "Matte finish stainless steel silencer with carbon end cap tailored for Aprilia urban max-scooters.",
        "price_inr": 28000,
        "hp_change": 1.2,
        "torque_change": 1.0,
        "weight_change": -1.8,
        "mileage_change": 0.0,
        "material": "AISI 304 Stainless Steel",
        "compatible_models": ["SR 160 Storm", "SXR 160 Maxi"]
    },

    # 2. Mirrors & Visibility
    {
        "name": "Rizoma Stealth Aero Winglet Bar-End Mirrors",
        "brand": "Rizoma",
        "cat": "mirrors",
        "desc": "Bi-functional winglet mirror that creates aerodynamic downforce at high speed while acting as rearview mirror.",
        "price_inr": 36000,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": -0.4,
        "mileage_change": 0.0,
        "material": "CNC Aluminum",
        "compatible_models": ["RS 457", "RS 660", "RSV4 Factory 1100"]
    },
    {
        "name": "CRG Hindsight LS Bar-End Folding Mirrors",
        "brand": "CRG",
        "cat": "mirrors",
        "desc": "Billet aluminum 3-inch round bar-end mirror with anti-glare convex glass and quick folding detent feature.",
        "price_inr": 18000,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": -0.3,
        "mileage_change": 0.0,
        "material": "6061-T6 Aluminum",
        "compatible_models": ["Tuono 660", "Tuono V4 Factory", "RS 457"]
    },
    {
        "name": "Doubletake Adventure Folding Mirrors Kit",
        "brand": "Doubletake",
        "cat": "mirrors",
        "desc": "Indestructible Zytel body folding mirror with RAM ball mount system engineered for extreme off-road rally conditions.",
        "price_inr": 14500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 0.1,
        "mileage_change": 0.0,
        "material": "Zytel Nylon Composite",
        "compatible_models": ["Tuareg 660 Rally"]
    },
    {
        "name": "CNC Anodized Aluminium Rearview Mirrors",
        "brand": "Rizoma",
        "cat": "mirrors",
        "desc": "Universal sleek rearview mirror set with tinted blue anti-glare glass and vibration damping stem.",
        "price_inr": 8500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": -0.2,
        "mileage_change": 0.0,
        "material": "Anodized Aluminum",
        "compatible_models": ["SR 160 Storm", "SXR 160 Maxi"]
    },

    # 3. Lighting & Headlights
    {
        "name": "Denali D4 TriOptic High-Output LED Auxiliary Light Kit",
        "brand": "Denali",
        "cat": "lights-auxiliary",
        "desc": "8760 lumens dual intensity LED pod light kit with spot & hybrid lenses for total night trail visibility.",
        "price_inr": 42000,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 1.2,
        "mileage_change": 0.0,
        "material": "Die-Cast Aluminum",
        "compatible_models": ["Tuareg 660 Rally"]
    },
    {
        "name": "Sequential Front & Rear LED Turn Signals Kit",
        "brand": "NRC",
        "cat": "lighting-headtail",
        "desc": "Ultra-bright sequential amber LED indicator light kit with smoked lenses for aggressive front profile.",
        "price_inr": 12500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": -0.2,
        "mileage_change": 0.0,
        "material": "Polycarbonate",
        "compatible_models": ["RS 457", "RS 660", "Tuono 660", "RSV4 Factory 1100", "Tuono V4 Factory"]
    },
    {
        "name": "Custom LED Tail Light with Integrated Indicators",
        "brand": "Custom LED",
        "cat": "lighting-headtail",
        "desc": "Plug and play clear lens tail light with programmable strobe pattern brake warning function.",
        "price_inr": 9500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": -0.1,
        "mileage_change": 0.0,
        "material": "ABS Plastics",
        "compatible_models": ["SR 160 Storm", "SXR 160 Maxi"]
    },

    # 4. Windshields & Aerodynamics
    {
        "name": "Puig Racing Double Bubble Windscreen",
        "brand": "Puig",
        "cat": "windshields-visors",
        "desc": "Aerodynamically tested acrylic windscreen providing superior wind deflection and reduced helmet buffeting.",
        "price_inr": 11500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 0.1,
        "mileage_change": 0.2,
        "material": "3mm High Impact Acrylic",
        "compatible_models": ["RS 457", "RS 660", "RSV4 Factory 1100"]
    },
    {
        "name": "Puig Touring Screen with Adjustable Visor",
        "brand": "Puig",
        "cat": "windshields-visors",
        "desc": "Tall touring windshield with multi-step adjustable upper spoiler for long distance adventure comfort.",
        "price_inr": 16500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 0.4,
        "mileage_change": 0.3,
        "material": "High Impact Polymer",
        "compatible_models": ["Tuareg 660 Rally"]
    },
    {
        "name": "Ermax High Protection Maxi Windshield",
        "brand": "Ermax",
        "cat": "windshields-visors",
        "desc": "Extended height windshield tailored for maxi-scooters to shield torso and shoulders from highway gusts.",
        "price_inr": 9800,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 0.3,
        "mileage_change": 0.1,
        "material": "Methacrylate",
        "compatible_models": ["SXR 160 Maxi", "SR 160 Storm"]
    },

    # 5. ECU & Tuning
    {
        "name": "UpMap T800+ ECU Flasher with Gabro Racing Map",
        "brand": "UpMap",
        "cat": "ecu-chips-tuning",
        "desc": "Smartphone controlled ECU flashing module pre-loaded with custom dyno tuned fuel & ignition maps.",
        "price_inr": 38000,
        "hp_change": 5.8,
        "torque_change": 4.1,
        "weight_change": 0.0,
        "mileage_change": -0.4,
        "material": "Electronics",
        "compatible_models": ["RS 660", "Tuono 660", "RSV4 Factory 1100", "Tuono V4 Factory", "Tuareg 660 Rally"]
    },
    {
        "name": "Dynojet Power Commander VI Fuel Controller",
        "brand": "Dynojet",
        "cat": "fuel-optimizers",
        "desc": "Precision fuel injection tuning module with dual axis mapping functionality for aftermarket exhausts.",
        "price_inr": 32000,
        "hp_change": 3.2,
        "torque_change": 2.5,
        "weight_change": 0.2,
        "mileage_change": -0.2,
        "material": "Electronics",
        "compatible_models": ["RS 457", "RS 660", "Tuono 660"]
    },

    # 6. High Performance Brakes
    {
        "name": "Brembo 19RCS Corsa Corta Radial Master Cylinder",
        "brand": "Brembo",
        "cat": "high-performance-brakes",
        "desc": "MotoGP technology radial brake master cylinder with adjustable bite point control (N, S, R).",
        "price_inr": 34000,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": -0.2,
        "mileage_change": 0.0,
        "material": "Forged Aluminum",
        "compatible_models": ["RSV4 Factory 1100", "Tuono V4 Factory", "RS 660"]
    },
    {
        "name": "Hel Performance Steel Braided Brake Lines Kit",
        "brand": "Hel Performance",
        "cat": "high-performance-brakes",
        "desc": "Full Teflon lined stainless steel braided brake hose kit ensuring zero expansion under hard lever pressure.",
        "price_inr": 11000,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": -0.3,
        "mileage_change": 0.0,
        "material": "Stainless Steel & PTFE",
        "compatible_models": ["RS 457", "RS 660", "RSV4 Factory 1100", "SR 160 Storm", "SXR 160 Maxi", "Tuareg 660 Rally", "Tuono 660", "Tuono V4 Factory"]
    },

    # 7. Crash Protection & Ergonomics
    {
        "name": "R&G Racing Aero Frame Sliders & Engine Case Covers",
        "brand": "R&G Racing",
        "cat": "bumpers-crash-guards",
        "desc": "High impact HDPE teardrop frame bobbins and engine case protectors preventing costly fairing damage in drops.",
        "price_inr": 19500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 0.8,
        "mileage_change": 0.0,
        "material": "HDPE & Aluminum",
        "compatible_models": ["RS 457", "RS 660", "Tuono 660", "RSV4 Factory 1100", "Tuono V4 Factory"]
    },
    {
        "name": "Hepco & Becker Heavy Duty Crash Guards & Skid Plate",
        "brand": "Hepco & Becker",
        "cat": "bumpers-crash-guards",
        "desc": "Tubular steel engine guard cage and 4mm aluminum sump guard engineered for extreme off-road rock protection.",
        "price_inr": 28500,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 3.4,
        "mileage_change": 0.0,
        "material": "Steel & 4mm Aluminum",
        "compatible_models": ["Tuareg 660 Rally"]
    },
    {
        "name": "Aprilia Ergonomic Comfort Gel Touring Seat",
        "brand": "Aprilia OEM",
        "cat": "touring-seats",
        "desc": "Official accessory seat with 3D gel inserts and anti-slip cover designed to reduce fatigue on long journeys.",
        "price_inr": 14000,
        "hp_change": 0.0,
        "torque_change": 0.0,
        "weight_change": 0.2,
        "mileage_change": 0.0,
        "material": "3D Gel & Vinyl",
        "compatible_models": ["RS 660", "Tuono 660", "Tuareg 660 Rally", "SXR 160 Maxi"]
    }
]

print("\n=== Inserting Aprilia Modification Parts & Linking Compatibility ===")
inserted_count = 0
compat_count = 0

for item in APRILIA_MODIFICATIONS:
    cat_slug = item["cat"]
    cat_id = cat_map.get(cat_slug)
    if not cat_id:
        print(f"Warning: Category slug {cat_slug} not found!")
        continue
        
    mod_id = str(uuid.uuid4()).replace("-", "")
    slug = item["name"].lower().replace(" ", "-").replace("(", "").replace(")", "").replace("&", "and").replace("+", "plus").replace("/", "-")
    
    cur.execute("""
        INSERT INTO modifications (
            id, category_id, brand_name, model_name, slug, description, short_description,
            price_inr, price_usd, hp_change_bhp, torque_change_nm, mileage_change_kmpl, weight_change_kg,
            material, warranty_months, average_rating, review_count, is_featured, requires_professional_install,
            is_legal_for_road, is_universal, is_active, is_deleted, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        mod_id, cat_id, item["brand"], item["name"], slug, item["desc"], item["desc"],
        item["price_inr"], round(item["price_inr"]/83.0, 2), item["hp_change"], item["torque_change"],
        item["mileage_change"], item["weight_change"], item["material"], 24, 4.8, 18, True, True,
        True, False, True, False
    ))
    inserted_count += 1
    
    # Link compatibility
    for model_name in item["compatible_models"]:
        vid = variant_map.get(model_name)
        if vid:
            compat_id = str(uuid.uuid4()).replace("-", "")
            cur.execute("""
                INSERT INTO modification_compatibility (
                    id, modification_id, variant_id, compatibility_type, notes, is_verified, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (compat_id, mod_id, vid, "DIRECT", f"Direct OEM/Performance bolt-on fitment for Aprilia {model_name}.", True))
            compat_count += 1

conn.commit()
conn.close()

print(f"\nSUCCESS: Inserted {inserted_count} modification parts and {compat_count} compatibility links for Aprilia models!")
