"""
MotoMod AI — User Build Configuration & Comparison Routing
Endpoints to CRUD personalized builds and run comparative evaluations.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.builds import UserBuild, BuildModification
from app.models.modifications import Modification
from app.schemas.builds import BuildCreateRequest, BuildResponse, BuildDetailResponse, CompareBuildsResponse
from app.api.v1.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/builds", tags=["User Configured Builds"])


@router.post(
    "",
    response_model=BuildResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and save a new custom motorcycle build configuration"
)
async def create_build(
    payload: BuildCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch modification objects to sum costs and specs
    mod_ids = [m.modification_id for m in payload.modifications]
    mods_res = await db.execute(select(Modification).filter(Modification.id.in_(mod_ids)))
    mods = mods_res.scalars().all()
    
    total_mod_cost = sum(m.price_inr or 0.0 for m in mods)
    total_install_cost = sum(m.installation_cost_inr or 0.0 for m in mods)

    # Calculate predicted specifications from offsets
    hp_gain = sum(m.hp_change_bhp or 0.0 for m in mods)
    torque_gain = sum(m.torque_change_nm or 0.0 for m in mods)
    mileage_gain = sum(m.mileage_change_kmpl or 0.0 for m in mods)

    # 2. Create the build record
    build = UserBuild(
        user_id=current_user.id,
        variant_id=payload.variant_id,
        name=payload.name,
        description=payload.description,
        is_public=payload.is_public,
        total_mod_cost_inr=total_mod_cost,
        total_install_cost_inr=total_install_cost,
        predicted_hp_bhp=hp_gain, # offsets stored for prediction heuristic
        predicted_torque_nm=torque_gain,
        predicted_mileage_kmpl=mileage_gain,
    )
    
    db.add(build)
    await db.flush()

    # 3. Associate build modifications
    for mod_item in payload.modifications:
        bm = BuildModification(
            build_id=build.id,
            modification_id=mod_item.modification_id,
            quantity=mod_item.quantity,
            notes=mod_item.notes
        )
        db.add(bm)
        
    await db.commit()
    await db.refresh(build)
    
    return build


@router.get(
    "",
    response_model=List[BuildResponse],
    summary="Get saved configurations for the authenticated user"
)
async def get_my_builds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(UserBuild).filter_by(user_id=current_user.id).order_by(UserBuild.created_at.desc())
    res = await db.execute(query)
    return res.scalars().all()


@router.get(
    "/{build_id}",
    response_model=BuildDetailResponse,
    summary="Retrieve full build layout details including catalog specs and accessories"
)
async def get_build_detail(
    build_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(UserBuild).filter_by(id=build_id, user_id=current_user.id)
    res = await db.execute(query)
    build = res.scalar_one_or_none()
    
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Build configuration not found."
        )
        
    return build


@router.get(
    "/compare/{build_a_id}/{build_b_id}",
    response_model=CompareBuildsResponse,
    summary="Compare two builds side-by-side"
)
async def compare_builds(
    build_a_id: UUID,
    build_b_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    a_res = await db.execute(select(UserBuild).filter_by(id=build_a_id, user_id=current_user.id))
    b_res = await db.execute(select(UserBuild).filter_by(id=build_b_id, user_id=current_user.id))
    
    a = a_res.scalar_one_or_none()
    b = b_res.scalar_one_or_none()
    
    if not a or not b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both builds not found."
        )

    comparison = {
        "horsepower_bhp": {"a": a.predicted_hp_bhp or 0.0, "b": b.predicted_hp_bhp or 0.0, "diff": (b.predicted_hp_bhp or 0.0) - (a.predicted_hp_bhp or 0.0)},
        "torque_nm": {"a": a.predicted_torque_nm or 0.0, "b": b.predicted_torque_nm or 0.0, "diff": (b.predicted_torque_nm or 0.0) - (a.predicted_torque_nm or 0.0)},
        "total_cost_inr": {"a": a.total_mod_cost_inr, "b": b.total_mod_cost_inr, "diff": b.total_mod_cost_inr - a.total_mod_cost_inr}
    }

    return {
        "build_a": a,
        "build_b": b,
        "metrics_comparison": comparison
    }
