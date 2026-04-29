"""
status_bar.py — Bottom status bar.

Left  : clock
Middle: device battery chips (device_id ≠ 0), local machine battery + charge
Right : 本地MQTT · 網絡MQTT · 數據綁定 · version
"""

import logging
try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False
    logging.getLogger(__name__).warning("psutil not installed — local battery unavailable")

from PySide6.QtCore    import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame

from ui.styles import (C_BG_SIDEBAR, C_BORDER, C_BORDER_MID,
                       C_TEXT_PRI, C_TEXT_SEC, C_TEXT_DIM,
                       C_NORMAL, C_ALARM, C_WARN, C_ACCENT)

VERSION = "v2.0.0"

log = logging.getLogger(__name__)


def _battery_colour(pct: int) -> str:
    if pct >= 50: return C_NORMAL
    if pct >= 20: return C_WARN
    return C_ALARM


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

        # {device_id: QLabel}  — created on demand
        self._dev_labels: dict[str, QLabel] = {}

        # ── Local machine battery ──────────────────────────────────
        self._batt_lay.addSpacing(4)
        self._lbl_local_batt = QLabel()
        self._lbl_local_batt.setStyleSheet(
            f"color:{C_TEXT_SEC}; font-size:8pt; background:transparent; border:none;"
        )
        self._batt_lay.addWidget(self._lbl_local_batt)

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
        """
        batteries: {device_id_str: percent}  (device_id "0" already excluded)
        Creates / updates small battery chip labels dynamically.
        """
        for dev_id, pct in sorted(batteries.items()):
            icon = _batt_icon(pct)
            colour = _battery_colour(pct)
            text = f"Dev{dev_id} {icon} {pct}%"
            if dev_id not in self._dev_labels:
                lbl = QLabel(text)
                lbl.setStyleSheet(
                    f"color:{colour}; font-size:8pt;"
                    " background:transparent; border:none; padding-right:6px;"
                )
                self._batt_lay.insertWidget(
                    self._batt_lay.count() - 2,  # before local battery
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
        """Read host machine battery via psutil and update label."""
        if not _PSUTIL:
            self._lbl_local_batt.setText("本機: N/A")
            return
        try:
            batt = psutil.sensors_battery()
            if batt is None:
                self._lbl_local_batt.setText("本機: 無電池")
                return
            pct       = int(batt.percent)
            charging  = batt.power_plugged
            icon      = "⚡" if charging else _batt_icon(pct)
            colour    = C_ACCENT if charging else _battery_colour(pct)
            charge_str = " 充電中" if charging else ""
            self._lbl_local_batt.setText(f"本機 {icon} {pct}%{charge_str}")
            self._lbl_local_batt.setStyleSheet(
                f"color:{colour}; font-size:8pt;"
                " background:transparent; border:none;"
            )
        except Exception as e:
            log.debug("Battery read error: %s", e)
            self._lbl_local_batt.setText("")


def _batt_icon(pct: int) -> str:
    if pct >= 80: return "🔋"
    if pct >= 50: return "🔋"
    if pct >= 20: return "🪫"
    return "🪫"
