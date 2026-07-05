"""
Configuration loader.

Reads config/config.yaml once and resolves every relative path against the
project root so the rest of the code can rely on absolute paths.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import yaml

# Project root = the folder that contains this src/ directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"

# Keys under `paths:` that should be turned into absolute Path objects.
_PATH_KEYS = (
    "raw_csv",
    "processed_parquet",
    "figures_dir",
    "tables_dir",
    "report_html",
    "log_file",
)


def load_config(path: str | Path | None = None) -> dict:
    """Load the YAML config and return it as a plain dict.

    All values under `paths:` are converted to absolute Path objects rooted at
    the project directory. A computed `current_year` and the derived
    `max_year` (current_year + max_year_offset) are injected for convenience.
    """
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Resolve every configured path to an absolute Path.
    paths = cfg.setdefault("paths", {})
    for key in _PATH_KEYS:
        if key in paths:
            paths[key] = (PROJECT_ROOT / paths[key]).resolve()

    # Inject helpers used by the cleaning step.
    current_year = dt.date.today().year
    cfg["cleaning"]["current_year"] = current_year
    cfg["cleaning"]["max_year"] = current_year + cfg["cleaning"].get("max_year_offset", 2)

    cfg["_project_root"] = PROJECT_ROOT
    return cfg


def ensure_dirs(cfg: dict) -> None:
    """Create every output directory referenced by the config if missing."""
    paths = cfg["paths"]
    for key in ("processed_parquet", "figures_dir", "tables_dir", "report_html", "log_file"):
        target = Path(paths[key])
        # For file paths, create the parent folder; for dir paths, the folder itself.
        folder = target.parent if target.suffix else target
        folder.mkdir(parents=True, exist_ok=True)
