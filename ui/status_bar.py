"""
status_bar.py — Bottom status bar.

Local battery is read by a background BatteryMonitor thread:
  - Polls every battery_check_interval seconds (configurable, default 30s)
  - BUT also checks the charging state every 1 second and fires immediately
    if power_plugged has changed (plug/unplug detected within ~1s)
  - Communicates to the Qt thread via a Qt signal (thread-safe)
"""

import logging
import threading
import time

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False
    logging.getLogger(__name__).warning("psutil not installed — local battery unavailable")

from PySide6.QtCore    import Qt, Signal, QObject
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame

from core.config import get
from ui.styles import (C_BG_SIDEBAR, C_BORDER, C_BORDER_MID,
                       C_TEXT_PRI, C_TEXT_SEC, C_TEXT_DIM,
                       C_NORMAL, C_ALARM, C_WARN, C_ACCENT)

VERSION = "v2.0.0"
log = logging.getLogger(__name__)


def _battery_colour(pct: int) -> str:
    if pct >= 50: return C_NORMAL
    if pct >= 20: return C_WARN
    return C_ALARM


def _batt_icon(pct: int, charging: bool) -> str:
    if charging: return "⚡"
    if pct >= 50: return "🔋"
    return "🪫"


# ── Battery monitor (background thread + Qt signal) ───────────────────────────

class _BatterySignals(QObject):
    """Carrier for the battery-update signal (must live in Qt thread)."""
    updated = Signal(str, str)   # (text, colour)


class BatteryMonitor:
    """
    Background thread that watches local battery.

    - Reads full battery info every `interval` seconds (configurable).
    - Checks power_plugged every 1 second; if it changes, fires immediately
      so plug/unplug is reflected within ~1 second regardless of interval.
    - Emits signals.updated(text, colour) — safe to connect to QLabel.
    """

    def __init__(self, interval: float = 30.0):
        self._interval   = max(1.0, float(interval))
        self.signals     = _BatterySignals()
        self._last_plug  = None   # last known power_plugged state
        self._running    = False
        self._thread: threading.Thread | None = None

    def start(self) -> "BatteryMonitor":
        if not _PSUTIL:
            self.signals.updated.emit("本機: N/A", C_TEXT_DIM)
            return self
        self._running = True
        self._thread = threading.Thread(
            target=self._run, name="batt_monitor", daemon=True
        )
        self._thread.start()
        return self

    def stop(self):
        self._running = False

    def _run(self):
        # Immediate first read so display is populated at startup
        self._read_and_emit()

        elapsed = 0.0
        while self._running:
            time.sleep(1.0)
            elapsed += 1.0

            # Always check plug state every second for instant change detection
            plug_changed = self._check_plug_changed()

            # Full update if: interval elapsed OR charging state just changed
            if plug_changed or elapsed >= self._interval:
                self._read_and_emit()
                if not plug_changed:
                    elapsed = 0.0
                else:
                    # Reset timer after a plug event too
                    elapsed = 0.0

    def _check_plug_changed(self) -> bool:
        """Return True if power_plugged state differs from last known."""
        try:
            batt = psutil.sensors_battery()
            if batt is None:
                return False
            current_plug = batt.power_plugged
            if self._last_plug is None:
                self._last_plug = current_plug
                return False
            if current_plug != self._last_plug:
                log.info("Battery charge state changed → %s",
                         "charging" if current_plug else "discharging")
                self._last_plug = current_plug
                return True
        except Exception:
            pass
        return False

    def _read_and_emit(self):
        try:
            batt = psutil.sensors_battery()
            if batt is None:
                self.signals.updated.emit("本機: 無電池", C_TEXT_DIM)
                return
            pct      = int(batt.percent)
            charging = batt.power_plugged
            self._last_plug = charging

            icon    = _batt_icon(pct, charging)
            colour  = C_ACCENT if charging else _battery_colour(pct)
            suffix  = " 充電中" if charging else ""
            text    = f"本機 {icon} {pct}%{suffix}"
            self.signals.updated.emit(text, colour)
            log.debug("Battery: %s  charging=%s", text, charging)
        except Exception as exc:
            log.debug("Battery read error: %s", exc)
            self.signals.updated.emit("", C_TEXT_DIM)


# ── StatusBar ─────────────────────────────────────────────────────────────────

class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("status_bar")
        self.setFixedHeight(32)
        self.setStyleSheet(
            f"#status_bar {{ background-color: {C_BG_SIDEBAR};"
            f" border-top: 1px solid {C_BORDER}; }}"
        )

        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(10, 0, 10, 0)
        self._lay.setSpacing(0)

        # ── Clock ──────────────────────────────────────────────────
        self._lbl_clock = QLabel("—")
        self._lbl_clock.setStyleSheet(
            f"color:{C_TEXT_PRI}; font-size:10pt; font-weight:bold;"
            " background:transparent; border:none;"
        )
        self._lay.addWidget(self._lbl_clock)

        self._lay.addSpacing(12)

        # ── Device battery area (dynamic labels) ───────────────────
        self._batt_frame = QWidget()
        self._batt_frame.setStyleSheet("background:transparent;")
        self._batt_lay = QHBoxLayout(self._batt_frame)
        self._batt_lay.setContentsMargins(0, 0, 0, 0)
        self._batt_lay.setSpacing(0)
        self._lay.addWidget(self._batt_frame)
        self._dev_labels: dict[str, QLabel] = {}

        # ── Local machine battery ──────────────────────────────────
        self._batt_lay.addSpacing(4)
        self._lbl_local_batt = QLabel()
        self._lbl_local_batt.setStyleSheet(
            f"color:{C_TEXT_SEC}; font-size:8pt; background:transparent; border:none;"
        )
        self._batt_lay.addWidget(self._lbl_local_batt)

        # Start battery monitor thread
        interval = float(get("battery_check_interval") or 30)
        self._batt_monitor = BatteryMonitor(interval=interval)
        self._batt_monitor.signals.updated.connect(self._on_battery_update)
        self._batt_monitor.start()

        self._lay.addStretch(1)

        # ── Status dots ────────────────────────────────────────────
        self._dot_priv = self._add_indicator("本地 MQTT")
        self._add_sep()
        self._dot_pub  = self._add_indicator("網絡 MQTT")
        self._add_sep()
        self._dot_bind = self._add_indicator("數據綁定")
        self._add_sep()

        lbl_ver = QLabel(VERSION)
        lbl_ver.setStyleSheet(
            f"color:{C_TEXT_DIM}; font-size:8pt; background:transparent; border:none;"
        )
        self._lay.addWidget(lbl_ver)
        self._lay.addSpacing(16)

    # ── Battery signal slot (Qt thread) ──────────────────────────────────────

    def _on_battery_update(self, text: str, colour: str) -> None:
        self._lbl_local_batt.setText(text)
        self._lbl_local_batt.setStyleSheet(
            f"color:{colour}; font-size:8pt; background:transparent; border:none;"
        )

    def stop_monitor(self) -> None:
        """Call on window close."""
        self._batt_monitor.stop()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _add_indicator(self, label: str) -> QLabel:
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color:{C_TEXT_SEC}; font-size:8pt;"
            " background:transparent; border:none; padding-right:3px;"
        )
        dot = QLabel("●")
        dot.setStyleSheet(
            f"color:{C_ALARM}; font-size:10pt; background:transparent; border:none;"
        )
        dot.setFixedWidth(16)
        dot.setAlignment(Qt.AlignCenter)
        self._lay.addSpacing(8)
        self._lay.addWidget(lbl)
        self._lay.addWidget(dot)
        return dot

    def _add_sep(self):
        sep = QLabel("·")
        sep.setStyleSheet(
            f"color:{C_BORDER}; font-size:14pt; background:transparent; border:none;"
        )
        self._lay.addSpacing(4)
        self._lay.addWidget(sep)
        self._lay.addSpacing(4)

    @staticmethod
    def _set_dot(dot: QLabel, on: bool):
        dot.setStyleSheet(
            f"color:{ C_NORMAL if on else C_ALARM }; font-size:10pt;"
            " background:transparent; border:none;"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def set_clock(self, s: str)          -> None: self._lbl_clock.setText(s)
    def set_private_mqtt(self, on: bool) -> None: self._set_dot(self._dot_priv, on)
    def set_public_mqtt(self, on: bool)  -> None: self._set_dot(self._dot_pub,  on)
    def set_bind_status(self, on: bool)  -> None: self._set_dot(self._dot_bind, on)

    def update_device_batteries(self, batteries: dict[str, int]) -> None:
        for dev_id, pct in sorted(batteries.items()):
            icon   = _batt_icon(pct, False)
            colour = _battery_colour(pct)
            text   = f"Dev{dev_id} {icon} {pct}%"
            if dev_id not in self._dev_labels:
                lbl = QLabel(text)
                lbl.setStyleSheet(
                    f"color:{colour}; font-size:8pt;"
                    " background:transparent; border:none; padding-right:6px;"
                )
                self._batt_lay.insertWidget(
                    self._batt_lay.count() - 2,
                    lbl
                )
                self._dev_labels[dev_id] = lbl
            else:
                lbl = self._dev_labels[dev_id]
                lbl.setText(text)
                lbl.setStyleSheet(
                    f"color:{colour}; font-size:8pt;"
                    " background:transparent; border:none; padding-right:6px;"
                )

    def update_local_battery(self) -> None:
        """No-op — battery is now updated by BatteryMonitor thread via signal."""
        pass

