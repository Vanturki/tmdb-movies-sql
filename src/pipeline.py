"""
Pipeline orchestrator.

Runs the full flow end to end, timing and logging every step:

    Load -> Validate(raw) -> Clean -> Validate(clean) -> EDA -> Visualize -> Report

Usage:
    python src/pipeline.py               # full run
    python src/pipeline.py --skip-clean  # reuse an existing cleaned parquet
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Make sibling modules importable whether run as a script or a module.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Windows terminals default to cp1252 and crash on Unicode; force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd

import clean as clean_mod
import eda as eda_mod
import report as report_mod
import validate as validate_mod
import visualize as viz_mod
from config import ensure_dirs, load_config
from logging_setup import setup_logging


def _step(logger, name):
    """Small context helper that logs a step's start, end and duration."""
    class _Ctx:
        def __enter__(self):
            self.t0 = time.perf_counter()
            logger.info("=== START: %s ===", name)
            return self

        def __exit__(self, exc_type, exc, tb):
            dt = time.perf_counter() - self.t0
            if exc_type is None:
                logger.info("=== DONE:  %s (%.1fs) ===", name, dt)
            else:
                logger.error("=== FAILED: %s (%.1fs): %s ===", name, dt, exc)
            return False
    return _Ctx()


def run(config_path=None, skip_clean=False) -> dict:
    cfg = load_config(config_path)
    ensure_dirs(cfg)
    logger = setup_logging(cfg["paths"]["log_file"])
    logger.info("Pipeline started for project: %s", cfg["project"]["name"])

    validation_reports = []

    # 1. Validate the raw file before we spend time cleaning it.
    with _step(logger, "Validate raw CSV"):
        validation_reports.append(validate_mod.validate_raw_csv(cfg, logger))

    # 2. Clean (DuckDB streams the 587 MB CSV -> compact parquet).
    parquet = Path(cfg["paths"]["processed_parquet"])
    if skip_clean and parquet.exists():
        logger.info("Skipping clean; reusing %s", parquet)
        cleaning_summary = {"raw_rows": 0, "clean_rows": 0, "dropped_rows": 0,
                            "pct_kept": 0.0, "note": "clean skipped"}
    else:
        with _step(logger, "Clean raw data"):
            cleaning_summary = clean_mod.clean_to_parquet(cfg, logger)
            pd.DataFrame([cleaning_summary]).to_csv(
                Path(cfg["paths"]["tables_dir"]) / "cleaning_summary.csv", index=False)

    # 3. Load the cleaned data (small subset of columns) for analysis.
    with _step(logger, "Load cleaned data"):
        df = eda_mod.load_clean(parquet)
        logger.info("Loaded %s cleaned rows", f"{len(df):,}")

    # 4. Validate the cleaned data.
    with _step(logger, "Validate cleaned data"):
        validation_reports.append(validate_mod.validate_clean_df(df, cfg, logger))

    # 5. EDA -> summary tables (also saved as CSVs).
    with _step(logger, "EDA / summary tables"):
        tables = eda_mod.run_eda(df, cfg)
        kpis = eda_mod.summary_kpis(df, cfg)
        tdir = Path(cfg["paths"]["tables_dir"])
        for name, tbl in tables.items():
            tbl.to_csv(tdir / f"{name}.csv", index=False)

    # 6. Charts.
    with _step(logger, "Visualize / charts"):
        figures = viz_mod.make_charts(tables, cfg, logger)

    # 7. HTML report.
    with _step(logger, "Build HTML report"):
        report_path = report_mod.build_report(
            kpis, cleaning_summary, validation_reports, figures, tables, cfg, logger)

    logger.info("Pipeline finished. Report: %s", report_path)
    return {"report": report_path, "kpis": kpis, "cleaning_summary": cleaning_summary}


def main():
    ap = argparse.ArgumentParser(description="TMDB movies analysis pipeline")
    ap.add_argument("--config", default=None, help="Path to config.yaml")
    ap.add_argument("--skip-clean", action="store_true",
                    help="Reuse an existing cleaned parquet instead of re-cleaning")
    args = ap.parse_args()
    run(config_path=args.config, skip_clean=args.skip_clean)


if __name__ == "__main__":
    main()
