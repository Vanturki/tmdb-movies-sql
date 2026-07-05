"""
Logging setup.

Configures a single logger that writes to both the console and a log file,
so every pipeline step and any error is recorded on disk (logs/pipeline.log).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_file: str | Path, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger writing to console + `log_file`.

    Safe to call more than once: existing handlers are cleared first so we do
    not attach duplicate handlers (which would print every line twice).
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("movies")
    logger.setLevel(level)
    logger.handlers.clear()          # avoid duplicate handlers on re-run
    logger.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler (stdout, UTF-8 friendly).
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler (appends across runs so history is kept).
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
