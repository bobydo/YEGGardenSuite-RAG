"""
Central logging setup for the app.

Usage:
    from service.log import configure_logging
    configure_logging()  # logs/<scriptname>.log + console

You can also override the script name:
    configure_logging(name="index_builder")  # logs/index_builder.log
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
from typing import Optional

from config import LOGS_DIR


def _infer_script_name() -> str:
    try:
        # Prefer the executable script path
        script = Path(sys.argv[0]) if sys.argv and sys.argv[0] else None
        if script and script.stem:
            return script.stem
    except Exception:
        pass
    # Fallbacks
    return "main"


def configure_logging(
    name: Optional[str] = None,
    level: int = logging.INFO,
    to_console: bool = True,
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
) -> logging.Logger:
    """Configure root logging with a rotating file handler under LOGS_DIR.

    - File: logs/<name>.log, where name defaults to the current script name.
    - Also attaches a console handler by default.
    - Safe to call multiple times: avoids duplicate handlers.
    """
    log_name = (name or _infer_script_name()) + ".log"
    log_path = LOGS_DIR / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    # Deduplicate: check if a handler already targets this file
    def _is_same_file_handler(h: logging.Handler) -> bool:
        try:
            return isinstance(h, RotatingFileHandler) and Path(getattr(h, "baseFilename", "")) == log_path
        except Exception:
            return False

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    if not any(_is_same_file_handler(h) for h in root.handlers):
        fh = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)

    if to_console and not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        root.addHandler(ch)

    return root
