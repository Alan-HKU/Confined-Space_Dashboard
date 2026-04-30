"""
app_paths.py — Resolves correct file paths for both dev and PyInstaller modes.

PyInstaller problem
-------------------
When packed as a one-file exe:
  - sys._MEIPASS  = temp dir where exe unpacks its bundled files (READ-ONLY)
  - sys.executable = path to the .exe file itself

The bundled config.ini inside _MEIPASS is read-only and discarded on exit.
User-editable config must live NEXT TO the exe, not inside it.

Resolution strategy
-------------------
  CONFIG_PATH  = writable user config, next to exe (or next to main.py in dev)
  ASSETS_PATH  = bundled assets inside _MEIPASS (or assets/ in dev)

On first launch of the packed exe, if no config.ini exists next to the exe,
we copy the bundled default config there so the user has an editable copy.
"""

import shutil
import sys
from pathlib import Path


def _is_frozen() -> bool:
    """True when running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def _exe_dir() -> Path:
    """Directory containing the .exe (frozen) or main.py (dev)."""
    if _is_frozen():
        return Path(sys.executable).parent.resolve()
    # Dev mode: go up from this file (core/) to project root
    return Path(__file__).parent.parent.resolve()


def _bundle_dir() -> Path:
    """Directory where PyInstaller unpacked bundled files (read-only)."""
    if _is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return _exe_dir()


# ── Public paths ──────────────────────────────────────────────────────────────

#: Writable config.ini — ALWAYS next to the exe / main.py
CONFIG_PATH: Path = _exe_dir() / "config.ini"

#: Read-only bundled assets (alarm.wav, icons, ...)
ASSETS_PATH: Path = _bundle_dir() / "assets"

#: Writable log file — next to exe / main.py
def log_path(filename: str = "Data.log") -> Path:
    return _exe_dir() / filename


def ensure_config() -> Path:
    """
    Guarantee CONFIG_PATH exists and is writable.

    If running as a packed exe and no config exists next to it yet,
    copy the bundled default from _MEIPASS so the user gets an editable copy.
    Returns the resolved CONFIG_PATH.
    """
    if not CONFIG_PATH.exists():
        bundled = _bundle_dir() / "config.ini"
        if bundled.exists() and bundled != CONFIG_PATH:
            shutil.copy2(str(bundled), str(CONFIG_PATH))
            import logging
            logging.getLogger(__name__).info(
                "First launch: copied default config → %s", CONFIG_PATH
            )
        # If bundled doesn't exist either, config.load() will just return defaults
    return CONFIG_PATH


def resolve_asset(filename: str) -> Path:
    """Return full path to an asset file (alarm.wav, Picture1.png, ...)."""
    return ASSETS_PATH / filename
