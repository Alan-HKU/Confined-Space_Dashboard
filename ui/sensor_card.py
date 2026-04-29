"""
sensor_card.py — Single sensor display card.

States
------
  WAITING  – no data ever received → card hidden (setVisible(False))
  LIVE     – data received, fresh   → normal / warn / alarm colour
  STALE    – data received, timeout → value shown as "—", grey text

The card becomes visible the first time update_display() is called with
value is not None.  It never goes back to hidden.
"""

from PySide6.QtCore    import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy

from core.data_model import SENSOR_WAITING, SENSOR_LIVE, SENSOR_ERROR, SENSOR_OFFLINE
from ui.styles import (C_WARN, C_ALARM, C_TEXT_SEC, C_TEXT_PRI,
                       C_TEXT_DIM, C_BG_CARD, C_BORDER, C_NORMAL, C_ACCENT2)

_LEVEL_VALUE_COLOUR = {
    "normal": C_TEXT_PRI,
    "warn":   C_WARN,
    "alarm":  C_ALARM,
}
_LEVEL_BORDER_COLOUR = {
    "normal": "#4a5066",   # brighter than C_BORDER to be clearly visible
    "warn":   C_WARN,
    "alarm":  C_ALARM,
}
_LEVEL_BORDER_WIDTH = {
    "normal": 1,
    "warn":   2,
    "alarm":  2,
}


class SensorCard(QWidget):
    """Single sensor card — hidden until first data arrives."""

    def __init__(self, sensor_key: str, meta: dict, parent=None):
        super().__init__(parent)
        self._key          = sensor_key
        self._meta         = meta
        self._level        = "normal"
        self._ever_received = False   # goes True on first non-None value

        self.setObjectName("sensor_card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()
        self._apply_card_style("normal", flash=False)

        # Hide until first data
        self.setVisible(False)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(2)

        # ── Top: name + device id ──
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(0)

        self._lbl_name = QLabel(self._meta.get("name", self._key))
        self._lbl_name.setObjectName("card_name")
        self._lbl_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._lbl_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Larger, bolder sensor name
        self._lbl_name.setStyleSheet(
            "font-size: 11pt; font-weight: 700; color: #dcdcdc;"
            " background: transparent; border: none;"
        )
        top.addWidget(self._lbl_name)

        self._lbl_device = QLabel("")
        self._lbl_device.setObjectName("card_device")
        self._lbl_device.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addWidget(self._lbl_device)

        root.addLayout(top)

        # ── Value ──
        self._lbl_value = QLabel("—")
        self._lbl_value.setObjectName("card_value")
        self._lbl_value.setAlignment(Qt.AlignCenter)
        self._lbl_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self._lbl_value)

        # ── Unit ──
        self._lbl_unit = QLabel(self._meta.get("unit", ""))
        self._lbl_unit.setObjectName("card_unit")
        self._lbl_unit.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        root.addWidget(self._lbl_unit)

    # ── Public API ────────────────────────────────────────────────────────────

    def update_display(
        self,
        value:         float | None,
        device_id:     str,
        level:         str,
        stale:         bool,          # kept for compat; use sensor_state when possible
        flash:         bool = False,
        has_timestamp: bool = False,
        sensor_state:  str  = SENSOR_WAITING,
    ) -> None:
        """Update the card. Shows on first MQTT message (any state except WAITING)."""

        if not self._ever_received and sensor_state != SENSOR_WAITING:
            self._ever_received = True
            self.setVisible(True)

        if not self._ever_received:
            return

        # ── Value text & colour based on sensor_state ─────────────────────
        if sensor_state == SENSOR_OFFLINE:
            self._lbl_value.setText("離線")
            val_colour = C_TEXT_DIM
            border_override = "#555a66"   # grey border for offline

        elif sensor_state == SENSOR_ERROR:
            # Error = sensor fault, value unavailable — show dash like normal no-data
            self._lbl_value.setText("—")
            val_colour = C_TEXT_SEC
            border_override = None

        elif value is None:
            self._lbl_value.setText("—")
            val_colour = C_TEXT_DIM
            border_override = None

        else:
            unit = self._meta.get("unit", "")
            if unit in ("exist", "alarm"):
                self._lbl_value.setText("是" if value >= 1 else "否")
            elif value == int(value):
                self._lbl_value.setText(str(int(value)))
            elif abs(value) < 10:
                self._lbl_value.setText(f"{value:.2f}")
            else:
                self._lbl_value.setText(f"{value:.1f}")
            val_colour     = _LEVEL_VALUE_COLOUR.get(level, C_TEXT_PRI)
            border_override = None

        self._lbl_value.setStyleSheet(
            f"font-size: 30pt; font-weight: bold; color: {val_colour};"
            f" background: transparent; border: none;"
        )

        self._lbl_device.setText(device_id or "")
        self._level = level
        self._apply_card_style(level, flash, border_override=border_override)

    def flash_toggle(self) -> None:
        if self._level == "alarm":
            self._flash_state = not getattr(self, "_flash_state", False)
            self._apply_card_style(self._level, self._flash_state)

    def _apply_card_style(self, level: str, flash: bool,
                          border_override: str | None = None) -> None:
        if border_override:
            bc = border_override
            bw = 1
        else:
            bc = _LEVEL_BORDER_COLOUR.get(level, "#4a5066")
            bw = _LEVEL_BORDER_WIDTH.get(level, 1)

        if flash and level == "alarm":
            bg = "rgba(255,85,85,0.12)"
        else:
            bg = C_BG_CARD  # slightly darker than panel = card feel

        self.setStyleSheet(
            f"#sensor_card {{"
            f"  background-color: {bg};"
            f"  border: {bw}px solid {bc};"
            f"  border-radius: 10px;"
            f"}}"
        )

