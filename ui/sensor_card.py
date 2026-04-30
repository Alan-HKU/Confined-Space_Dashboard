"""
sensor_card.py — High-end sensor card with reliable border rendering.

Uses QFrame as the outer shell so border + border-radius render correctly
in Qt (QWidget needs WA_StyledBackground which has side effects; QFrame
renders styled borders reliably out of the box).

Layout:
  QFrame #sensor_card_frame  ← border + border-radius painted here
    └─ QVBoxLayout (no margins, spacing=0)
         ├─ accent_bar  QFrame  3px coloured top strip
         └─ body QWidget
               ├─ header row: name  +  device
               ├─ separator 1px
               ├─ value label (large, centred, expands)
               └─ unit label
"""

from PySide6.QtCore    import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QSizePolicy, QFrame)

from core.data_model import SENSOR_WAITING, SENSOR_LIVE, SENSOR_ERROR, SENSOR_OFFLINE
from ui.styles import C_WARN, C_ALARM, C_TEXT_PRI, C_TEXT_DIM, C_TEXT_SEC

# ── Design tokens ─────────────────────────────────────────────────────────────
_PANEL_BG = "#1c1f26"    # main panel (grid background)

_CARD_BG = {
    "normal":  "#252a35",   # clearly lighter than panel → card pops
    "warn":    "#2c2a1a",
    "alarm":   "#2c1a1a",
    "offline": "#20232c",
    "error":   "#22252e",
}
_ACCENT = {
    "normal":  "#4a5270",
    "warn":    "#d4c040",
    "alarm":   "#cc3333",
    "offline": "#3a3f52",
    "error":   "#3a3f52",
}
_BORDER = {
    "normal":  "#3e4560",
    "warn":    "#807830",
    "alarm":   "#803030",
    "offline": "#30354a",
    "error":   "#35394e",
}
_VALUE_COLOUR = {
    "normal":  "#e8eaf0",
    "warn":    "#f1fa8c",
    "alarm":   "#ff5555",
    "offline": "#505870",
    "error":   "#606680",
}


class SensorCard(QWidget):
    """Sensor card — hidden until first MQTT message arrives."""

    def __init__(self, sensor_key: str, meta: dict, parent=None):
        super().__init__(parent)
        self._key           = sensor_key
        self._meta          = meta
        self._level         = "normal"
        self._ever_received = False

        # Dirty-check cache
        self._last_text   = ""
        self._last_colour = ""
        self._last_dev    = ""
        self._last_cstate = ""
        self._last_flash  = False

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()
        self.setVisible(False)

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── QFrame shell: this is where border + border-radius is applied ──
        self._frame = QFrame(self)
        self._frame.setObjectName("sensor_card_frame")
        self._frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._frame.setFrameShape(QFrame.StyledPanel)   # enables styled painting
        outer.addWidget(self._frame)

        frame_lay = QVBoxLayout(self._frame)
        frame_lay.setContentsMargins(0, 0, 0, 0)
        frame_lay.setSpacing(0)

        # ── Top accent bar ──
        self._accent = QFrame()
        self._accent.setObjectName("card_accent")
        self._accent.setFixedHeight(4)
        frame_lay.addWidget(self._accent)

        # ── Body ──
        body = QWidget()
        body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(16, 8, 16, 12)
        body_lay.setSpacing(0)

        # Header: name + device id
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 0)
        hdr.setSpacing(4)

        self._lbl_name = QLabel(self._meta.get("name", self._key))
        self._lbl_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._lbl_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hdr.addWidget(self._lbl_name)

        self._lbl_device = QLabel("")
        self._lbl_device.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hdr.addWidget(self._lbl_device)

        body_lay.addLayout(hdr)
        body_lay.addSpacing(6)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setObjectName("card_sep")
        body_lay.addWidget(sep)

        # Value — large, centred, thin weight
        self._lbl_value = QLabel("—")
        self._lbl_value.setAlignment(Qt.AlignCenter)
        self._lbl_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_lay.addWidget(self._lbl_value)

        # Unit
        self._lbl_unit = QLabel(self._meta.get("unit", ""))
        self._lbl_unit.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        body_lay.addWidget(self._lbl_unit)
        body_lay.addSpacing(2)

        frame_lay.addWidget(body, 1)

        # Apply initial style
        self._apply("normal")

    # ── Public API ─────────────────────────────────────────────────────────────

    def update_display(
        self,
        value:         float | None,
        device_id:     str,
        level:         str,
        stale:         bool,
        flash:         bool = False,
        has_timestamp: bool = False,
        sensor_state:  str  = SENSOR_WAITING,
    ) -> None:
        if not self._ever_received and sensor_state != SENSOR_WAITING:
            self._ever_received = True
            self.setVisible(True)
        if not self._ever_received:
            return

        # Determine card state
        if sensor_state == SENSOR_OFFLINE:
            cstate   = "offline"
            new_text = "離線"
        elif sensor_state == SENSOR_ERROR:
            cstate   = "error"
            new_text = "—"
        elif value is None:
            cstate   = "normal"
            new_text = "—"
        else:
            unit = self._meta.get("unit", "")
            if unit in ("exist", "alarm"):
                new_text = "是" if value >= 1 else "否"
            elif value == int(value):
                new_text = str(int(value))
            elif abs(value) < 10:
                new_text = f"{value:.2f}"
            else:
                new_text = f"{value:.1f}"
            cstate = level

        colour = _VALUE_COLOUR.get(cstate, "#e8eaf0")

        # Dirty-check
        if new_text != self._last_text:
            self._lbl_value.setText(new_text)
            self._last_text = new_text

        if colour != self._last_colour:
            self._lbl_value.setStyleSheet(
                f"font-size: 38pt; font-weight: 200; color: {colour};"
                " background: transparent; border: none; letter-spacing: -2px;"
            )
            self._last_colour = colour

        dev = device_id or ""
        if dev != self._last_dev:
            self._lbl_device.setText(dev)
            self._last_dev = dev

        if cstate != self._last_cstate or flash != self._last_flash:
            self._apply(cstate, flash)
            self._last_cstate = cstate
            self._last_flash  = flash

        self._level = level

    def flash_toggle(self) -> None:
        if self._level == "alarm":
            self._last_flash = not self._last_flash
            self._apply("alarm", self._last_flash)

    # ── Styling ────────────────────────────────────────────────────────────────

    def _apply(self, cstate: str, flash: bool = False) -> None:
        bg     = _CARD_BG.get(cstate, _CARD_BG["normal"])
        accent = _ACCENT.get(cstate, _ACCENT["normal"])
        border = _BORDER.get(cstate, _BORDER["normal"])

        if flash and cstate == "alarm":
            bg     = "#3a1515"
            accent = "#ff2222"
            border = "#cc2222"

        # ── Frame: full border + radius ──
        self._frame.setStyleSheet(
            f"QFrame#sensor_card_frame {{"
            f"  background-color: {bg};"
            f"  border: 1px solid {border};"
            f"  border-top: none;"          # accent bar sits above
            f"  border-bottom-left-radius: 8px;"
            f"  border-bottom-right-radius: 8px;"
            f"  border-top-left-radius: 0px;"
            f"  border-top-right-radius: 0px;"
            f"}}"
        )

        # ── Accent bar ──
        self._accent.setStyleSheet(
            f"QFrame#card_accent {{"
            f"  background-color: {accent};"
            f"  border: none;"
            f"  border-top-left-radius: 8px;"
            f"  border-top-right-radius: 8px;"
            f"  border-bottom: none;"
            f"}}"
        )

        # ── Clear all child styles so they inherit transparent ──
        self._frame.setStyleSheet(
            self._frame.styleSheet() +
            "QFrame#sensor_card_frame QWidget { background: transparent; border: none; }"
            "QFrame#sensor_card_frame QLabel  { background: transparent; border: none; }"
            "QFrame#sensor_card_frame QFrame[objectName='card_sep'] {"
            "  background-color: #303550; border: none; }"
        )

        # Name label
        name_alpha = "rgba(160,168,190,0.85)" if cstate == "offline" else "#a0a8be"
        self._lbl_name.setStyleSheet(
            f"font-size: 25pt; font-weight: 600; letter-spacing: 0.3px;"
            f" color: {name_alpha}; background: transparent; border: none;"
        )

        # Device label
        self._lbl_device.setStyleSheet(
            f"font-size: 7pt; color: #404860;"
            " background: transparent; border: none;"
        )

        # Unit label
        unit_colour = "#404860" if cstate in ("offline", "error") else "#505878"
        self._lbl_unit.setStyleSheet(
            f"font-size: 15pt; color: {unit_colour}; letter-spacing: 0.8px;"
            " background: transparent; border: none;"
        )

        # Initial value label style if not yet set
        if not self._last_colour:
            self._lbl_value.setStyleSheet(
                "font-size: 38pt; font-weight: 200; color: #e8eaf0;"
                " background: transparent; border: none; letter-spacing: -2px;"
            )
