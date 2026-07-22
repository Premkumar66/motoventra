"""
BikeVerse AI — Dataset Collector CLI Utility
Command line tool to launch dataset collection, deduplication, and export routines.
Usage:
  python -m app.collector.cli --full
  python -m app.collector.cli --brand ktm
  python -m app.collector.cli --export-only
  python -m app.collector.cli --dedupe
"""
import sys
import argparse
import json
from app.collector.pipeline import BikeVerseDatasetPipeline
from app.collector.processors.deduplicator import ImageDeduplicator
from app.collector.processors.exporter import DatasetExporter


def main():
    parser = argparse.ArgumentParser(description="BikeVerse AI — Global Motorcycle Dataset Collector CLI")
    parser.add_argument("--full", action="store_true", help="Run full automated dataset collection pipeline")
    parser.add_argument("--limit-brands", type=int, default=None, help="Limit maximum number of brands to process")
    parser.add_argument("--export-only", action="store_true", help="Re-generate CSV, JSON, SQLite, and MongoDB exports")
    parser.add_argument("--dedupe", action="store_true", help="Run image deduplication and quality check")

    args = parser.parse_args()
    pipeline = BikeVerseDatasetPipeline()

    if args.export_only:
        print("Re-generating export files...")
        exporter = DatasetExporter()
        paths = exporter.export_all()
        print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))
    elif args.dedupe:
        print("Running image deduplication check...")
        deduper = ImageDeduplicator()
        stats = deduper.process_directory()
        print(json.dumps(stats, indent=2))
    else:
        # Default or --full run
        print("Running BikeVerse AI full collection pipeline...")
        summary = pipeline.run_full_pipeline(brand_limit=args.limit_brands)
        print("\n" + "=" * 60)
        print("BIKEVERSE AI PIPELINE EXECUTION SUMMARY")
        print("=" * 60)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
