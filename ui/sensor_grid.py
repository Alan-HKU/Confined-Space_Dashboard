"""
sensor_grid.py — Home page sensor grid.

Layout rules
------------
- Always 2 rows × 6 columns (fixed grid, never stretches weirdly)
- Total 12 slots (matches the 12 non-cam sensors)
- "cam" sensor is excluded — no card created for it
- Cards are HIDDEN until their first MQTT message arrives
- When fewer than 6 cards are visible, empty placeholder slots fill the
  remaining columns so visible cards are never stretched to fill the row
- Cards appear in arrival order: first-received → top-left, left→right
"""

import logging
from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy, QFrame

from ui.sensor_card import SensorCard
from ui.styles import C_BG_PANEL, C_BORDER

log = logging.getLogger(__name__)

ROWS    = 2
COLS    = 6
SLOTS   = ROWS * COLS   # 12
EXCLUDE = {"cam"}


def _placeholder() -> QWidget:
    """Invisible spacer that holds a grid cell open."""
    w = QFrame()
    w.setStyleSheet(
        f"background-color: transparent; border: none;"
    )
    w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return w


class SensorGrid(QWidget):
    """Fixed 2×6 grid. Cards appear as data arrives; empty slots stay open."""

    def __init__(self, sensor_meta: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        self._sensor_meta  = sensor_meta
        self._cards: dict[str, SensorCard] = {}
        self._arrival_order: list[str] = []

        # Build fixed 2×6 grid
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(12)

        # Explicit background so cards contrast against it
        self.setStyleSheet(f"background-color: #1c1f26;")

        # Equal stretch on all cols and rows — never changes
        for col in range(COLS):
            self._layout.setColumnStretch(col, 1)
        for row in range(ROWS):
            self._layout.setRowStretch(row, 1)

        # Fill all 12 slots with placeholder widgets initially
        self._placeholders: dict[int, QWidget] = {}
        for slot in range(SLOTS):
            row, col = divmod(slot, COLS)
            ph = _placeholder()
            self._layout.addWidget(ph, row, col)
            self._placeholders[slot] = ph

        # Pre-create all sensor cards (hidden), excluding 'cam'
        for key, meta in sensor_meta.items():
            if key in EXCLUDE:
                continue
            card = SensorCard(key, meta, parent=self)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            card.setVisible(False)
            self._cards[key] = card

    # ── Public API ────────────────────────────────────────────────────────────

    def update_sensor(
        self,
        key:           str,
        value,
        device_id:     str,
        level:         str,
        stale:         bool,
        flash:         bool = False,
        has_timestamp: bool = False,
        sensor_state:  str  = "waiting",
    ) -> None:
        if key in EXCLUDE:
            return
        card = self._cards.get(key)
        if card is None:
            return

        was_visible = card.isVisible()

        card.update_display(value, device_id, level, stale, flash,
                            has_timestamp=has_timestamp,
                            sensor_state=sensor_state)

        # First time card becomes visible → place it in the next available slot
        if not was_visible and card.isVisible():
            if key not in self._arrival_order:
                self._arrival_order.append(key)
                self._place_card(key)

    def flash_alarm_cards(self) -> None:
        for card in self._cards.values():
            card.flash_toggle()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _place_card(self, key: str) -> None:
        """
        Place card into the next empty slot, replacing its placeholder.
        The grid dimensions never change — only the content of each cell does.
        """
        slot = self._arrival_order.index(key)
        if slot >= SLOTS:
            log.warning("More cards than slots (%d), skipping %s", SLOTS, key)
            return

        row, col = divmod(slot, COLS)
        card = self._cards[key]

        # Remove the placeholder from this slot
        ph = self._placeholders.pop(slot, None)
        if ph is not None:
            self._layout.removeWidget(ph)
            ph.deleteLater()

        # Add the real card into the same slot
        self._layout.addWidget(card, row, col)
        log.debug("Grid: placed %s at [%d,%d]  (%d visible)",
                  key, row, col, len(self._arrival_order))
