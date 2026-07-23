import sys

path = r'c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\api\v1\routes\bikes.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

new_endpoints = '''

@router.get(
    "/variants/{variant_id}/full-details",
    summary="Get complete bike details including images, 3D models, compatible parts, and predictions"
)
async def get_variant_full_details(
    variant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Returns all sections needed for the Bike Detail view."""
    from app.models.modifications import Modification, ModificationCompatibility, ModificationCategoryModel
    from sqlalchemy import or_
    
    # Load variant with motorcycle and brand
    q = select(MotorcycleVariant).options(
        selectinload(MotorcycleVariant.motorcycle).selectinload(Motorcycle.brand),
        selectinload(MotorcycleVariant.images)
    ).filter_by(id=variant_id, is_active=True)
    res = await db.execute(q)
    variant = res.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="Motorcycle variant not found.")
    
    # Load compatible modifications grouped by category
    compat_subq = (
        select(ModificationCompatibility.modification_id)
        .where(ModificationCompatibility.variant_id == variant_id)
        .scalar_subquery()
    )
    mods_q = select(Modification).options(
        selectinload(Modification.category),
        selectinload(Modification.images)
    ).where(
        Modification.is_active == True,
        or_(Modification.id.in_(compat_subq), Modification.is_universal == True)
    )
    mods_res = await db.execute(mods_q)
    all_mods = mods_res.scalars().all()
    
    # Group mods by category
    mods_by_category = {}
    for mod in all_mods:
        cat_name = mod.category.name if mod.category else "Other"
        cat_slug = mod.category.slug if mod.category else "other"
        if cat_slug not in mods_by_category:
            mods_by_category[cat_slug] = {"category_name": cat_name, "category_slug": cat_slug, "items": []}
        mods_by_category[cat_slug]["items"].append({
            "id": str(mod.id),
            "brand_name": mod.brand_name,
            "model_name": mod.model_name,
            "price_inr": mod.price_inr,
            "hp_change_bhp": mod.hp_change_bhp,
            "torque_change_nm": mod.torque_change_nm,
            "mileage_change_kmpl": mod.mileage_change_kmpl,
            "material": mod.material,
            "image_url": mod.images[0].url if mod.images else None,
            "is_universal": mod.is_universal,
        })
    
    moto = variant.motorcycle
    brand = moto.brand if moto else None
    
    # Build images list
    images = [
        {
            "url": img.url,
            "thumbnail_url": img.thumbnail_url,
            "alt_text": img.alt_text,
            "color_name": img.color_name,
            "image_type": img.image_type,
            "is_primary": img.is_primary,
            "sort_order": img.sort_order,
        }
        for img in sorted(variant.images, key=lambda x: (not x.is_primary, x.sort_order))
    ]
    
    # Determine primary image
    primary_image = None
    if hasattr(variant, 'primary_image_url') and variant.primary_image_url:
        primary_image = variant.primary_image_url
    elif images:
        primary_image = images[0]["url"]
    else:
        primary_image = f"/api/v1/bikes/placeholder/{brand.slug if brand else 'unknown'}/{moto.slug if moto else 'unknown'}"
    
    return {
        "id": str(variant.id),
        "variant_name": variant.variant_name,
        "year": variant.year,
        "primary_image": primary_image,
        "three_d_model_url": getattr(variant, 'three_d_model_url', None),
        "spin_360_urls": getattr(variant, 'spin_360_urls', None) or [],
        "images": images,
        "brand": {"id": str(brand.id), "name": brand.name, "slug": brand.slug, "logo_url": brand.logo_url} if brand else None,
        "model": {"id": str(moto.id), "name": moto.name, "slug": moto.slug, "category": moto.category.value if moto else None} if moto else None,
        "specs": {
            "engine_cc": variant.engine_cc,
            "engine_type": variant.engine_type,
            "cylinders": variant.cylinders,
            "fuel_type": variant.fuel_type.value if variant.fuel_type else None,
            "horsepower_bhp": variant.horsepower_bhp,
            "horsepower_rpm": variant.horsepower_rpm,
            "torque_nm": variant.torque_nm,
            "torque_rpm": variant.torque_rpm,
            "top_speed_kmh": variant.top_speed_kmh,
            "mileage_kmpl": variant.mileage_kmpl,
            "mileage_city_kmpl": variant.mileage_city_kmpl,
            "mileage_highway_kmpl": variant.mileage_highway_kmpl,
            "acceleration_0_100": variant.acceleration_0_100,
            "transmission": variant.transmission.value if variant.transmission else None,
            "gear_count": variant.gear_count,
            "weight_kg": variant.weight_kg,
            "kerb_weight_kg": variant.kerb_weight_kg,
            "wheelbase_mm": variant.wheelbase_mm,
            "seat_height_mm": variant.seat_height_mm,
            "ground_clearance_mm": variant.ground_clearance_mm,
            "fuel_tank_liters": variant.fuel_tank_liters,
            "front_suspension": variant.front_suspension,
            "rear_suspension": variant.rear_suspension,
            "front_brake": variant.front_brake,
            "rear_brake": variant.rear_brake,
            "has_abs": variant.has_abs,
            "abs_type": variant.abs_type,
            "front_tyre": variant.front_tyre,
            "rear_tyre": variant.rear_tyre,
            "instrument_cluster": variant.instrument_cluster,
            "headlight_type": variant.headlight_type,
            "has_led_tail": variant.has_led_tail,
            "has_traction_control": variant.has_traction_control,
            "has_ride_modes": variant.has_ride_modes,
            "has_quickshifter": variant.has_quickshifter,
            "has_bluetooth": variant.has_bluetooth,
            "electronics_features": variant.electronics_features,
            "price_inr": variant.price_inr,
            "price_usd": variant.price_usd,
            "official_colors": variant.official_colors,
        },
        "compatible_parts": list(mods_by_category.values()),
    }


@router.get(
    "/placeholder/{brand_slug}/{model_slug}",
    summary="Dynamic SVG placeholder image for bikes without photos"
)
async def get_bike_placeholder(
    brand_slug: str,
    model_slug: str,
):
    from fastapi.responses import Response
    brand_name = brand_slug.replace("-", " ").title()
    model_name = model_slug.replace("-", " ").title()
    
    svg = f\'\'\'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#060b18"/>
      <stop offset="100%" style="stop-color:#0d1525"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00f2fe"/>
      <stop offset="100%" style="stop-color:#9b51e0"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="800" height="500" fill="url(#bg)"/>
  <circle cx="400" cy="220" r="120" fill="none" stroke="url(#accent)" stroke-width="1" opacity="0.2"/>
  <circle cx="400" cy="220" r="80" fill="none" stroke="url(#accent)" stroke-width="1" opacity="0.15"/>
  <!-- Motorcycle silhouette -->
  <g transform="translate(400,220)" opacity="0.5" filter="url(#glow)">
    <!-- Wheels -->
    <circle cx="-120" cy="60" r="55" fill="none" stroke="#00f2fe" stroke-width="4"/>
    <circle cx="-120" cy="60" r="30" fill="none" stroke="#00f2fe" stroke-width="2"/>
    <circle cx="120" cy="60" r="55" fill="none" stroke="#9b51e0" stroke-width="4"/>
    <circle cx="120" cy="60" r="30" fill="none" stroke="#9b51e0" stroke-width="2"/>
    <!-- Frame -->
    <line x1="-65" y1="60" x2="65" y2="60" stroke="#00f2fe" stroke-width="6" stroke-linecap="round"/>
    <line x1="-40" y1="60" x2="0" y2="-40" stroke="#00f2fe" stroke-width="5" stroke-linecap="round"/>
    <line x1="40" y1="60" x2="0" y2="-40" stroke="#9b51e0" stroke-width="5" stroke-linecap="round"/>
    <!-- Engine -->
    <rect x="-25" y="-10" width="50" height="40" rx="6" fill="none" stroke="#6b7fa8" stroke-width="3"/>
    <!-- Seat -->
    <path d="M -30,-40 Q 0,-60 40,-40" fill="none" stroke="#00f2fe" stroke-width="5" stroke-linecap="round"/>
    <!-- Handlebars -->
    <line x1="-50" y1="-45" x2="-20" y2="-45" stroke="#6b7fa8" stroke-width="3" stroke-linecap="round"/>
    <!-- Fork -->
    <line x1="-70" y1="10" x2="-120" y2="60" stroke="#6b7fa8" stroke-width="4"/>
    <line x1="-80" y1="10" x2="-120" y2="60" stroke="#6b7fa8" stroke-width="4"/>
  </g>
  <!-- Brand label -->
  <text x="400" y="370" text-anchor="middle" font-family="Arial,sans-serif" font-size="28" font-weight="900" fill="url(#accent)">{brand_name}</text>
  <text x="400" y="400" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" fill="#6b7fa8">{model_name}</text>
  <!-- Bottom label -->
  <text x="400" y="460" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="rgba(107,127,168,0.6)" letter-spacing="3">IMAGE COMING SOON</text>
  <!-- Top accent line -->
  <rect x="0" y="0" width="800" height="3" fill="url(#accent)" opacity="0.7"/>
</svg>\'\'\'
    return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

'''

with open(path, 'a', encoding='utf-8') as f:
    f.write(new_endpoints)

print("Task 4 done")
