import sys, re

# TASK 3
path = r'c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\api\v1\routes\modifications.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add from sqlalchemy import or_ if not present
if 'from sqlalchemy import or_' not in text:
    if 'from sqlalchemy import select, func' in text:
        text = text.replace('from sqlalchemy import select, func', 'from sqlalchemy import select, func, or_')
    else:
        text = 'from sqlalchemy import or_\n' + text

new_endpoint = '''@router.get(
    "/accessories",
    summary="List modification accessories with optional variant and category filtering"
)
async def get_accessories(
    variant_id: Optional[UUID] = Query(None, description="Filter by motorcycle variant compatibility"),
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    from app.models.modifications import ModificationCompatibility, ModificationCategoryModel
    offset = (page - 1) * per_page
    
    if variant_id:
        # Strict filtering: only parts compatible with this variant OR universal parts
        compat_subq = (
            select(ModificationCompatibility.modification_id)
            .where(ModificationCompatibility.variant_id == variant_id)
            .scalar_subquery()
        )
        base_query = (
            select(Modification)
            .where(
                Modification.is_active == True,
                or_(
                    Modification.id.in_(compat_subq),
                    Modification.is_universal == True
                )
            )
        )
    else:
        base_query = select(Modification).where(Modification.is_active == True)
    
    if category_slug:
        cat_subq = select(ModificationCategoryModel.id).where(ModificationCategoryModel.slug == category_slug).scalar_subquery()
        base_query = base_query.where(Modification.category_id.in_(cat_subq))
    
    if featured is not None:
        base_query = base_query.where(Modification.is_featured == featured)
    
    count_res = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_res.scalar() or 0
    
    items_res = await db.execute(
        base_query.options(
            selectinload(Modification.category),
            selectinload(Modification.images)
        ).order_by(Modification.is_featured.desc(), Modification.brand_name.asc()).offset(offset).limit(per_page)
    )
    items = items_res.scalars().all()
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "items": [
            {
                "id": str(m.id),
                "category_id": str(m.category_id),
                "category": {"id": str(m.category.id), "name": m.category.name, "slug": m.category.slug} if m.category else None,
                "brand_name": m.brand_name,
                "model_name": m.model_name,
                "slug": m.slug,
                "short_description": m.short_description,
                "price_inr": m.price_inr,
                "price_usd": m.price_usd,
                "hp_change_bhp": m.hp_change_bhp,
                "torque_change_nm": m.torque_change_nm,
                "mileage_change_kmpl": m.mileage_change_kmpl,
                "weight_change_kg": m.weight_change_kg,
                "material": m.material,
                "warranty_months": m.warranty_months,
                "is_featured": m.is_featured,
                "is_legal_for_road": m.is_legal_for_road,
                "is_universal": m.is_universal,
                "image_url": m.images[0].url if m.images else None,
            }
            for m in items
        ],
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }'''

text = re.sub(r'@router\.get\(\n\s*\"/accessories\".*?return \{.*?\}', new_endpoint, text, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Task 3 done')
