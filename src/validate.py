"""
Data validation gates.

Two gates guard the pipeline:
  1. validate_raw_csv  -> before cleaning (schema + row count on the raw file)
  2. validate_clean_df -> after cleaning  (nulls, ranges, duplicates)

Each returns a ValidationReport. When cfg['validation']['hard_fail'] is True a
failing report raises ValidationError; otherwise the pipeline logs and continues.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import duckdb
import pandas as pd


class ValidationError(Exception):
    """Raised when a validation gate fails and hard_fail is enabled."""


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class ValidationReport:
    gate: str
    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append(Check(name, passed, detail))

    @property
    def ok(self) -> bool:
        return all(c.passed for c in self.checks)

    def failures(self) -> list[Check]:
        return [c for c in self.checks if not c.passed]

    def summary(self) -> str:
        status = "PASS" if self.ok else "FAIL"
        lines = [f"[{status}] {self.gate} ({len(self.failures())} failing)"]
        for c in self.checks:
            mark = "ok " if c.passed else "XX "
            lines.append(f"  {mark} {c.name}: {c.detail}")
        return "\n".join(lines)


def _finish(report: ValidationReport, cfg: dict, logger=None) -> ValidationReport:
    """Log the report and raise if hard_fail is on and it failed."""
    if logger:
        for line in report.summary().splitlines():
            (logger.info if report.ok else logger.warning)(line)
    if not report.ok and cfg["validation"].get("hard_fail", False):
        raise ValidationError(f"{report.gate} failed: {[c.name for c in report.failures()]}")
    return report


def validate_raw_csv(cfg: dict, logger=None) -> ValidationReport:
    """Check the raw CSV has the required columns and enough rows."""
    v = cfg["validation"]
    raw_csv = str(cfg["paths"]["raw_csv"])
    report = ValidationReport(gate="raw")

    con = duckdb.connect()
    try:
        cols = [
            r[0]
            for r in con.execute(
                f"DESCRIBE SELECT * FROM read_csv('{raw_csv}', all_varchar=true, "
                f"header=true, ignore_errors=true)"
            ).fetchall()
        ]
        missing = [c for c in v["required_columns"] if c not in cols]
        report.add("required_columns", not missing,
                   "all present" if not missing else f"missing: {missing}")

        n_rows = con.execute(
            f"SELECT count(*) FROM read_csv('{raw_csv}', all_varchar=true, "
            f"header=true, ignore_errors=true)"
        ).fetchone()[0]
        report.add("min_raw_rows", n_rows >= v["min_raw_rows"],
                   f"{n_rows:,} rows (floor {v['min_raw_rows']:,})")
    finally:
        con.close()

    return _finish(report, cfg, logger)


def validate_clean_df(df: pd.DataFrame, cfg: dict, logger=None) -> ValidationReport:
    """Check the cleaned DataFrame: no key nulls, sane ranges, no duplicate ids."""
    v = cfg["validation"]
    report = ValidationReport(gate="clean")

    # Enough rows survived cleaning.
    report.add("min_clean_rows", len(df) >= v["min_clean_rows"],
               f"{len(df):,} rows (floor {v['min_clean_rows']:,})")

    # No nulls in key columns.
    for col in ("id", "title", "release_date"):
        n_null = int(df[col].isna().sum()) if col in df.columns else -1
        report.add(f"no_null_{col}", n_null == 0, f"{n_null} nulls")

    # Ratings within [rating_min, rating_max].
    if "vote_average" in df.columns:
        va = df["vote_average"].dropna()
        in_range = bool(((va >= v["rating_min"]) & (va <= v["rating_max"])).all())
        report.add("rating_in_range", in_range,
                   f"min={va.min():.1f} max={va.max():.1f}" if len(va) else "no data")

    # No negative runtime.
    if "runtime" in df.columns:
        rt = df["runtime"].dropna()
        report.add("runtime_non_negative", bool((rt >= 0).all()),
                   f"min={rt.min():.0f}" if len(rt) else "no data")

    # id is unique.
    if "id" in df.columns:
        n_dupe = int(df["id"].duplicated().sum())
        report.add("unique_id", n_dupe == 0, f"{n_dupe} duplicate ids")

    return _finish(report, cfg, logger)
