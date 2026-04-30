"""
alarm_controller.py — Manages alarm sound and border flashing.

Uses QSoundEffect for low-latency looping audio (must be created after
QApplication). Flash state is toggled every call so the caller decides
the tick rate (typically the GUI refresh timer).
"""

import os
import logging
from pathlib import Path

from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore       import QUrl

from core.config import get

log = logging.getLogger(__name__)


class AlarmController:
    """Manages alarm audio and flash-state toggling."""

    def __init__(self):
        self._audio_enabled   = bool(get("audio_playing") if get("audio_playing") is not None else True)
        self._flash_enabled   = bool(get("alarm_border_flash") if get("alarm_border_flash") is not None else True)
        self._alarm_active    = False
        self._flash_state     = False

        # Resolve alarm sound via app_paths (works in both dev and frozen exe)
        from core.app_paths import resolve_asset
        sound_file = get("alarm_sound_file") or "alarm.wav"
        resolved_path = resolve_asset(sound_file)
        resolved = resolved_path if resolved_path.exists() else None

        self._sound = QSoundEffect()
        if self._audio_enabled and resolved:
            self._sound.setSource(QUrl.fromLocalFile(str(resolved.resolve())))
            self._sound.setLoopCount(-2)
            self._sound.setVolume(1.0)
            log.info("Alarm sound loaded: %s", resolved)
        elif self._audio_enabled:
            log.warning("Alarm sound file not found: %s", sound_file)

    # ── Public API ────────────────────────────────────────────────────────────

    def tick(self, alarm_active: bool) -> bool:
        """
        Call once per GUI refresh tick.

        Returns the current flash state (True = bright, False = dim).
        Handles play/stop transitions automatically.
        """
        if alarm_active != self._alarm_active:
            self._alarm_active = alarm_active
            if alarm_active:
                self._start_alarm()
            else:
                self._stop_alarm()

        if alarm_active and self._flash_enabled:
            self._flash_state = not self._flash_state
        else:
            self._flash_state = False

        return self._flash_state

    def stop(self) -> None:
        """Force stop alarm (e.g. on app exit)."""
        self._stop_alarm()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _start_alarm(self):
        log.info("Alarm STARTED")
        if self._audio_enabled and self._sound.isLoaded():
            self._sound.play()

    def _stop_alarm(self):
        log.info("Alarm STOPPED")
        if self._audio_enabled:
            self._sound.stop()
        self._flash_state = False
