"""
BikeVerse AI — Dataset Collector Routing
FastAPI endpoints to trigger dataset collection, monitor status, and download exports.
"""
import os
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

from app.collector.pipeline import BikeVerseDatasetPipeline
from app.collector.config import DATASET_DIR, EXPORTS_DIR, CSV_EXPORT_PATH, JSON_EXPORT_PATH, SQLITE_EXPORT_PATH, MONGO_EXPORT_PATH
from app.collector.processors.exporter import DatasetExporter

router = APIRouter(prefix="/collector", tags=["Dataset Collector Engine"])

pipeline = BikeVerseDatasetPipeline()
collector_state = {
    "is_running": False,
    "last_run_summary": None
}


def _run_background_pipeline(brand_limit: int = None):
    collector_state["is_running"] = True
    try:
        summary = pipeline.run_full_pipeline(brand_limit=brand_limit)
        collector_state["last_run_summary"] = summary
    finally:
        collector_state["is_running"] = False


@router.post(
    "/trigger",
    summary="Trigger full background dataset collection pipeline"
)
async def trigger_collection(
    background_tasks: BackgroundTasks,
    limit_brands: int = None
):
    if collector_state["is_running"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dataset collector pipeline is currently already executing."
        )

    background_tasks.add_task(_run_background_pipeline, limit_brands)
    return {
        "message": "BikeVerse AI Dataset Collection Pipeline started in background.",
        "status": "initiated"
    }


@router.get(
    "/status",
    summary="Get dataset collection status, model counts, and export paths"
)
async def get_collector_status():
    exporter = DatasetExporter()
    records = exporter.load_dataset_records()

    return {
        "is_running": collector_state["is_running"],
        "total_brands": len(records.get("brands", [])),
        "total_models": len(records.get("models", [])),
        "total_image_assets": sum(len(m.get("image_paths", [])) for m in records.get("models", [])),
        "last_summary": collector_state["last_run_summary"],
        "export_files": {
            "csv": str(CSV_EXPORT_PATH),
            "json": str(JSON_EXPORT_PATH),
            "sqlite": str(SQLITE_EXPORT_PATH),
            "mongo": str(MONGO_EXPORT_PATH)
        }
    }


@router.get(
    "/export/{export_format}",
    summary="Download dataset export file (csv, json, sqlite, mongo)"
)
async def download_export(export_format: str):
    fmt = export_format.lower()
    path_map = {
        "csv": CSV_EXPORT_PATH,
        "json": JSON_EXPORT_PATH,
        "sqlite": SQLITE_EXPORT_PATH,
        "mongo": MONGO_EXPORT_PATH
    }

    if fmt not in path_map:
        raise HTTPException(status_code=400, detail="Invalid format. Use csv, json, sqlite, or mongo.")

    target_path = path_map[fmt]
    if not target_path.exists():
        # Generate exports if missing
        exporter = DatasetExporter()
        exporter.export_all()

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found.")

    return FileResponse(
        path=target_path,
        filename=target_path.name,
        media_type="application/octet-stream"
    )
