"""
alarm_controller.py — Manages alarm sound and border flashing.

Linux audio strategy (in order of preference):
  1. QSoundEffect — fastest, lowest latency, needs GStreamer
  2. QMediaPlayer  — more compatible GStreamer usage
  3. subprocess → aplay / paplay / ffplay — pure system, no Qt audio needed

Windows: QSoundEffect works reliably (DirectSound backend).

The controller tries each method in order and logs which one succeeded.
"""

import logging
import os
import subprocess
import sys
import threading
from pathlib import Path

from PySide6.QtCore       import QUrl
from PySide6.QtMultimedia import QSoundEffect

from core.config import get

log = logging.getLogger(__name__)


# ── Platform helpers ──────────────────────────────────────────────────────────

def _find_player() -> tuple[str, list[str]] | None:
    """Return (player_name, base_args) for the first available system player."""
    candidates = [
        ("aplay",   []),           # ALSA — standard Linux
        ("paplay",  []),           # PulseAudio
        ("pw-play", []),           # PipeWire
        ("ffplay",  ["-nodisp", "-autoexit", "-loglevel", "quiet"]),
        ("afplay",  []),           # macOS
    ]
    for name, args in candidates:
        try:
            subprocess.run(["which", name],
                           check=True, capture_output=True)
            return name, args
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None


class _SubprocessPlayer:
    """Plays a WAV file in a loop using a system command (no Qt audio needed)."""

    def __init__(self, wav_path: str):
        self._path    = wav_path
        self._player  = _find_player()
        self._proc: subprocess.Popen | None = None
        self._running = False
        self._thread: threading.Thread | None = None

        if self._player:
            log.info("Linux audio fallback: using %s", self._player[0])
        else:
            log.warning("No system audio player found (tried aplay/paplay/ffplay)")

    @property
    def available(self) -> bool:
        return self._player is not None

    def play(self):
        if not self.available or self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self._proc = None

    def _loop(self):
        name, base_args = self._player
        cmd = [name] + base_args + [self._path]
        while self._running:
            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._proc.wait()
            except Exception as exc:
                log.error("Audio subprocess error: %s", exc)
                break


# ── AlarmController ───────────────────────────────────────────────────────────

class AlarmController:
    """Manages alarm audio (cross-platform) and border flash state."""

    def __init__(self):
        self._audio_enabled = bool(
            get("audio_playing") if get("audio_playing") is not None else True
        )
        self._flash_enabled = bool(
            get("alarm_border_flash") if get("alarm_border_flash") is not None else True
        )
        self._alarm_active = False
        self._flash_state  = False

        # Resolve sound file
        from core.app_paths import resolve_asset
        sound_file    = get("alarm_sound_file") or "alarm.wav"
        resolved_path = resolve_asset(sound_file)
        self._wav_path = str(resolved_path) if resolved_path.exists() else None

        if self._audio_enabled and not self._wav_path:
            log.warning("Alarm sound file not found: %s", sound_file)

        # ── Audio backend selection ──────────────────────────────────────────
        self._qt_sound:  QSoundEffect | None     = None
        self._sys_sound: _SubprocessPlayer | None = None

        if self._audio_enabled and self._wav_path:
            self._init_audio()

    def _init_audio(self):
        """Try QSoundEffect first; fall back to system player on Linux."""
        # ── Try QSoundEffect ──────────────────────────────────────────────────
        try:
            se = QSoundEffect()
            se.setSource(QUrl.fromLocalFile(self._wav_path))
            se.setLoopCount(-2)   # infinite
            se.setVolume(1.0)

            # On Linux, QSoundEffect may silently fail — check status
            # We consider it valid only if it reports no error
            # (status is checked lazily; we'll verify in _start_alarm)
            self._qt_sound = se
            log.info("Audio: QSoundEffect loaded  %s", self._wav_path)

        except Exception as exc:
            log.warning("QSoundEffect init failed: %s", exc)
            self._qt_sound = None

        # ── Also prepare system fallback (Linux only) ─────────────────────────
        if sys.platform != "win32":
            sp = _SubprocessPlayer(self._wav_path)
            if sp.available:
                self._sys_sound = sp
                log.info("Audio fallback ready: %s", _find_player()[0] if _find_player() else "none")

    # ── Public API ────────────────────────────────────────────────────────────

    def tick(self, alarm_active: bool) -> bool:
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

    def stop(self):
        self._stop_alarm()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _start_alarm(self):
        log.info("Alarm STARTED")
        if not self._audio_enabled:
            return

        played = False

        # Try QSoundEffect
        if self._qt_sound is not None:
            try:
                self._qt_sound.play()
                # Give it a moment to actually start (async)
                # If it's in error state, fall through to system player
                from PySide6.QtMultimedia import QSoundEffect as _SE
                status = self._qt_sound.status()
                # Status 3 = Error; 0 = Null; 1 = Loading; 2 = Ready
                if status != 3:   # not error → assume OK
                    played = True
                    log.debug("Audio: QSoundEffect playing (status=%d)", status)
                else:
                    log.warning("QSoundEffect status=Error, trying system fallback")
                    self._qt_sound.stop()
            except Exception as exc:
                log.warning("QSoundEffect play failed: %s", exc)

        # Fall back to system player
        if not played and self._sys_sound is not None:
            self._sys_sound.play()
            log.info("Audio: system player fallback active")

    def _stop_alarm(self):
        log.info("Alarm STOPPED")

        if self._qt_sound is not None:
            try:
                self._qt_sound.stop()
            except Exception:
                pass

        if self._sys_sound is not None:
            self._sys_sound.stop()

        self._flash_state = False
