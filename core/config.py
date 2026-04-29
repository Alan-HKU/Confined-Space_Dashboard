"""
config.py — Configuration loader for Confined Space Monitoring System.

Reads config.ini once at startup. All modules import get() / get_sensor()
instead of touching configparser directly.
"""

import ast
import configparser
import os
from pathlib import Path

_cfg = configparser.RawConfigParser()
_loaded = False

# ── Public interface ─────────────────────────────────────────────────────────

def load(path: str | Path = "config.ini") -> None:
    """Load (or reload) the configuration file. Must be called before get()."""
    global _loaded
    _cfg.read(path, encoding="utf-8")
    _loaded = True


def get(key: str, section: str = "GENERAL", fallback=None):
    """Return a typed value from the config.

    Tries GENERAL → CONNECTION → SENSOR in order when section is 'GENERAL'.
    Strings that look like Python literals (lists, bools, ints, floats) are
    evaluated automatically.
    """
    if not _loaded:
        load()

    # Auto-search all sections if default
    sections = [section] if section != "GENERAL" else ["GENERAL", "CONNECTION", "SENSOR"]
    raw = None
    for sec in sections:
        if _cfg.has_option(sec, key):
            raw = _cfg.get(sec, key)
            break

    if raw is None:
        return fallback

    raw = raw.strip()

    # Strip surrounding quotes for plain strings
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]

    # Try Python literal evaluation (lists, bools, ints, floats)
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw


def get_sensor() -> dict:
    """Return a structured dict with all sensor metadata."""
    keys    = get("sensor",        section="SENSOR") or []
    names   = get("display_name",  section="SENSOR") or []
    lv1     = get("min_max_lv1",   section="SENSOR") or []
    lv2     = get("min_max_lv2",   section="SENSOR") or []
    units   = get("unit",          section="SENSOR") or []
    enabled = get("alarm_enabled", section="SENSOR") or []

    sensors = {}
    for i, key in enumerate(keys):
        sensors[key] = {
            "index":         i,
            "name":          names[i]   if i < len(names)   else key,
            "lv1":           lv1[i]     if i < len(lv1)     else [0, 9999],
            "lv2":           lv2[i]     if i < len(lv2)     else [0, 9999],
            "unit":          units[i]   if i < len(units)    else "",
            "alarm_enabled": bool(enabled[i]) if i < len(enabled) else True,
        }
    return sensors
