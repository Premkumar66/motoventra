"""
MotoMod AI — Bike Image Dataset Management API Endpoints
Comprehensive REST API for image collection, validation, search, administration, and exports.
"""
import io
import csv
import json
from typing import Optional, List
from uuid import UUID

from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Response, status
)
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.image_dataset import (
    BikeImageBrand, BikeImageModel, BikeModelYear, BikeImage, BikeImageMetadata,
    ImageViewType, ImageStatus, ImportSource
)
from app.services.image_dataset import (
    storage_service, collector_service, ai_service, validator_service
)

router = APIRouter(prefix="/images", tags=["Bike Image Dataset"])


# ─── 1. LIST IMAGES ──────────────────────────────────────────────────────────
@router.get("", summary="Get all motorcycle images with filtering and pagination")
async def list_images(
    brand: Optional[str] = Query(None, description="Filter by brand name or slug"),
    model: Optional[str] = Query(None, description="Filter by model name or slug"),
    year: Optional[int] = Query(None, description="Filter by model year"),
    view_type: Optional[str] = Query(None, description="Filter by view type (front, rear, etc.)"),
    status_val: Optional[str] = Query("approved", description="Filter by status (approved, pending, etc.)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(BikeImage).join(BikeImageModel, BikeImage.model_id == BikeImageModel.id)

    if status_val and status_val.lower() != "all":
        query = query.where(BikeImage.status == ImageStatus(status_val.lower()))

    if view_type:
        query = query.where(BikeImage.view_type == ImageViewType(view_type.lower()))

    if model:
        query = query.where(or_(
            BikeImageModel.slug.ilike(f"%{model}%"),
            BikeImageModel.name.ilike(f"%{model}%")
        ))

    if brand:
        query = query.join(BikeImageBrand, BikeImageModel.brand_id == BikeImageBrand.id)\
                     .where(or_(
                         BikeImageBrand.slug.ilike(f"%{brand}%"),
                         BikeImageBrand.name.ilike(f"%{brand}%")
                     ))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total_items = total_res.scalar() or 0

    # Paginate
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    res = await db.execute(query)
    images = res.scalars().all()

    items = []
    for img in images:
        # Get Model and Brand info
        res_m = await db.execute(select(BikeImageModel).where(BikeImageModel.id == img.model_id))
        m_obj = res_m.scalar_one_or_none()
        b_name = "Unknown"
        m_name = m_obj.name if m_obj else "Unknown"
        if m_obj:
            res_b = await db.execute(select(BikeImageBrand).where(BikeImageBrand.id == m_obj.brand_id))
            b_obj = res_b.scalar_one_or_none()
            if b_obj:
                b_name = b_obj.name

        yr = 2024
        if img.year_record_id:
            res_y = await db.execute(select(BikeModelYear).where(BikeModelYear.id == img.year_record_id))
            y_obj = res_y.scalar_one_or_none()
            if y_obj:
                yr = y_obj.year

        items.append({
            "id": str(img.id),
            "brand": b_name,
            "model": m_name,
            "year": yr,
            "view_type": img.view_type.value if img.view_type else "other",
            "file_name": img.file_name,
            "file_url": img.file_url,
            "thumbnail_url": f"/static/dataset_images/{img.thumbnail_path}" if img.thumbnail_path else img.file_url,
            "preview_url": f"/static/dataset_images/{img.preview_path}" if img.preview_path else img.file_url,
            "width": img.width,
            "height": img.height,
            "file_size_bytes": img.file_size_bytes,
            "status": img.status.value,
            "is_verified": img.is_verified,
            "created_at": img.created_at.isoformat() if img.created_at else None
        })

    return {
        "items": items,
        "meta": {
            "total": total_items,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_items + per_page - 1) // per_page if total_items > 0 else 1
        }
    }


# ─── 2. STATS OVERVIEW ───────────────────────────────────────────────────────
@router.get("/stats", summary="Get overall dataset statistics")
async def get_dataset_stats(db: AsyncSession = Depends(get_db)):
    tot_imgs = (await db.execute(select(func.count(BikeImage.id)))).scalar() or 0
    tot_brands = (await db.execute(select(func.count(BikeImageBrand.id)))).scalar() or 0
    tot_models = (await db.execute(select(func.count(BikeImageModel.id)))).scalar() or 0
    tot_pending = (await db.execute(select(func.count(BikeImage.id)).where(BikeImage.status == ImageStatus.PENDING))).scalar() or 0
    tot_approved = (await db.execute(select(func.count(BikeImage.id)).where(BikeImage.status == ImageStatus.APPROVED))).scalar() or 0

    return {
        "total_images": tot_imgs,
        "total_brands": tot_brands,
        "total_models": tot_models,
        "approved_images": tot_approved,
        "pending_approval": tot_pending
    }


# ─── 3. MISSING IMAGES REPORT ────────────────────────────────────────────────
@router.get("/missing", summary="Get report of models missing required image views")
async def get_missing_images(db: AsyncSession = Depends(get_db)):
    return await ai_service.analyze_missing_images(db)


# ─── 4. SEARCH IMAGES ────────────────────────────────────────────────────────
@router.get("/search", summary="Search images by multiple metadata criteria")
async def search_images(
    query_str: Optional[str] = Query(None, description="Free text brand/model search"),
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    view_type: Optional[str] = Query(None),
    min_width: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(BikeImage).join(BikeImageModel, BikeImage.model_id == BikeImageModel.id)

    if query_str:
        query = query.where(or_(
            BikeImageModel.name.ilike(f"%{query_str}%"),
            BikeImage.file_name.ilike(f"%{query_str}%")
        ))

    if min_width:
        query = query.where(BikeImage.width >= min_width)

    if view_type:
        query = query.where(BikeImage.view_type == ImageViewType(view_type.lower()))

    res = await db.execute(query.limit(50))
    images = res.scalars().all()

    results = []
    for img in images:
        results.append({
            "id": str(img.id),
            "file_name": img.file_name,
            "file_url": img.file_url,
            "view_type": img.view_type.value,
            "width": img.width,
            "height": img.height
        })
    return {"results": results, "count": len(results)}


# ─── 5. UPLOAD IMAGE (ADMIN) ──────────────────────────────────────────────────
@router.post("/upload", summary="Upload an image directly into the dataset")
async def upload_image(
    file: UploadFile = File(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(2024),
    view_type: str = Form("front"),
    attribution: Optional[str] = Form("Admin Upload"),
    db: AsyncSession = Depends(get_db)
):
    file_bytes = await file.read()
    ok, msg, bike_img = await collector_service.ingest_image_bytes(
        db=db,
        file_bytes=file_bytes,
        brand_name=brand,
        model_name=model,
        year=year,
        view_type=view_type,
        source_type=ImportSource.ADMIN_UPLOAD,
        attribution=attribution
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    return {"status": "success", "message": msg, "image_id": str(bike_img.id), "file_url": bike_img.file_url}


# ─── 6. IMPORT FROM URL ───────────────────────────────────────────────────────
@router.post("/import/url", summary="Import a bike image from a public URL")
async def import_url(
    url: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(2024),
    view_type: str = Form("front"),
    attribution: Optional[str] = Form("URL Import"),
    db: AsyncSession = Depends(get_db)
):
    ok, msg, bike_img = await collector_service.import_from_url(
        db=db,
        url=url,
        brand_name=brand,
        model_name=model,
        year=year,
        view_type=view_type,
        attribution=attribution
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    return {"status": "success", "message": msg, "image_id": str(bike_img.id), "file_url": bike_img.file_url}


# ─── 7. IMPORT FROM CSV ───────────────────────────────────────────────────────
@router.post("/import/csv", summary="Batch import dataset from CSV file")
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    content = (await file.read()).decode("utf-8")
    result = await collector_service.import_from_csv(db, content)
    return result


# ─── 8. IMPORT FROM WIKIMEDIA ─────────────────────────────────────────────────
@router.post("/import/wikimedia", summary="Collect open media from Wikimedia Commons")
async def import_wikimedia(
    query: str = Query("Royal Enfield", description="Search topic on Wikimedia Commons"),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    return await collector_service.import_from_wikimedia(db, query=query, limit=limit)


# ─── 9. APPROVE IMAGE ────────────────────────────────────────────────────────
@router.put("/{image_id}/approve", summary="Approve a pending image")
async def approve_image(image_id: UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BikeImage).where(BikeImage.id == image_id))
    img = res.scalar_one_or_none()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    img.status = ImageStatus.APPROVED
    img.is_verified = True
    db.add(img)
    await db.commit()
    return {"status": "success", "message": f"Image {image_id} approved"}


# ─── 10. REJECT IMAGE ────────────────────────────────────────────────────────
@router.put("/{image_id}/reject", summary="Reject a pending image")
async def reject_image(
    image_id: UUID,
    reason: Optional[str] = Query("Low quality or inaccurate view"),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(BikeImage).where(BikeImage.id == image_id))
    img = res.scalar_one_or_none()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    img.status = ImageStatus.REJECTED
    img.rejection_reason = reason
    db.add(img)
    await db.commit()
    return {"status": "success", "message": f"Image {image_id} rejected"}


# ─── 11. DELETE IMAGE ────────────────────────────────────────────────────────
@router.delete("/{image_id}", summary="Delete an image record and file")
async def delete_image(image_id: UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BikeImage).where(BikeImage.id == image_id))
    img = res.scalar_one_or_none()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete filesystem file
    storage_service.delete_image_file(img.file_path)

    await db.delete(img)
    await db.commit()
    return {"status": "success", "message": f"Image {image_id} deleted"}


# ─── 12. EXPORT METADATA AS CSV ───────────────────────────────────────────────
@router.get("/export/csv", summary="Export complete image metadata dataset as CSV")
async def export_metadata_csv(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BikeImage))
    images = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "File Name", "File Path", "File URL", "View Type",
        "Width", "Height", "File Size Bytes", "SHA256 Hash", "Status"
    ])

    for img in images:
        writer.writerow([
            str(img.id), img.file_name, img.file_path, img.file_url,
            img.view_type.value if img.view_type else "",
            img.width, img.height, img.file_size_bytes,
            img.image_hash, img.status.value if img.status else ""
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bikeverse_image_dataset.csv"}
    )


# ─── 13. EXPORT METADATA AS JSON ──────────────────────────────────────────────
@router.get("/export/json", summary="Export complete image metadata dataset as JSON")
async def export_metadata_json(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BikeImage))
    images = res.scalars().all()

    export_data = []
    for img in images:
        export_data.append({
            "id": str(img.id),
            "file_name": img.file_name,
            "file_path": img.file_path,
            "file_url": img.file_url,
            "view_type": img.view_type.value if img.view_type else "other",
            "width": img.width,
            "height": img.height,
            "file_size_bytes": img.file_size_bytes,
            "image_hash": img.image_hash,
            "status": img.status.value if img.status else "pending"
        })

    return Response(
        content=json.dumps(export_data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=bikeverse_image_dataset.json"}
    )
