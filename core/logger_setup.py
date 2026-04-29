"""
logger_setup.py — Centralised logging configuration.

Platform notes
--------------
Windows: ANSI colour codes are supported on Windows 10 1903+ (with VT100 enabled)
         and in Windows Terminal. For older cmd.exe we fall back to plain formatter.
Linux:   Full ANSI support assumed.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _ansi_supported() -> bool:
    """Return True if the current terminal supports ANSI escape codes."""
    if sys.platform == "win32":
        # Windows 10 1903+ supports VT100 in conhost; Windows Terminal always does.
        # Check TERM_PROGRAM first (set by Windows Terminal, VS Code etc.)
        if os.environ.get("TERM_PROGRAM") or os.environ.get("WT_SESSION"):
            return True
        # Try enabling VT100 on stdout via ctypes
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode   = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                new_mode = mode.value | 0x0004
                if kernel32.SetConsoleMode(handle, new_mode):
                    return True
        except Exception:
            pass
        return False
    # Linux / macOS — assume ANSI support if stdout is a tty
    return sys.stdout.isatty()


def setup_logging(
    log_path:     str  = "Data.log",
    max_bytes:    int  = 5 * 1024 * 1024,
    backup_count: int  = 5,
    console_level: int = logging.DEBUG,
    file_level:    int = logging.INFO,
) -> None:
    """Configure root logger: coloured console + rotating file handler."""

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fmt_detail = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    fmt_file   = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_fmt   = "%Y-%m-%d %H:%M:%S"

    # ── Console handler ──────────────────────────────────────────────────────
    con = logging.StreamHandler(sys.stdout)
    con.setLevel(console_level)
    if _ansi_supported():
        con.setFormatter(_ColouredFormatter(fmt_detail, datefmt=date_fmt))
    else:
        con.setFormatter(logging.Formatter(fmt_detail, datefmt=date_fmt))
    root.addHandler(con)

    # ── Rotating file handler ────────────────────────────────────────────────
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    rfh = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    rfh.setLevel(file_level)
    rfh.setFormatter(logging.Formatter(fmt_file, datefmt=date_fmt))
    root.addHandler(rfh)

    logging.info(
        "Logging started — console: %s, file: %s (max %d KB × %d)",
        logging.getLevelName(console_level), log_file,
        max_bytes // 1024, backup_count,
    )


class _ColouredFormatter(logging.Formatter):
    _COLOURS = {
        logging.DEBUG:    "\033[36m",   # Cyan
        logging.INFO:     "\033[32m",   # Green
        logging.WARNING:  "\033[33m",   # Yellow
        logging.ERROR:    "\033[31m",   # Red
        logging.CRITICAL: "\033[35m",   # Magenta
    }
    _RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self._COLOURS.get(record.levelno, "")
        record.levelname = f"{colour}{record.levelname}{self._RESET}"
        return super().format(record)
