"""
sensor_grid.py — Home page sensor grid.

Layout rules
------------
- 6 columns, up to 2 rows (12 sensors total without cam)
- "cam" sensor is excluded — no card created for it
- Cards are HIDDEN until their first MQTT message arrives
- Cards appear in arrival order (first-received appears first, left→right, top→bottom)
  achieved by tracking arrival_order and re-laying grid on each new card reveal
"""

import logging
from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy

from ui.sensor_card import SensorCard

log = logging.getLogger(__name__)

COLS    = 6
EXCLUDE = {"cam"}      # sensors to skip entirely


class SensorGrid(QWidget):
    """2×6 grid of sensor cards. Cards appear as data arrives."""

    def __init__(self, sensor_meta: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        self._sensor_meta   = sensor_meta
        self._cards: dict[str, SensorCard] = {}
        self._arrival_order: list[str] = []   # keys in the order they first appeared

        # Pre-create all cards (hidden), excluding 'cam'
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)
        for col in range(COLS):
            self._layout.setColumnStretch(col, 1)

        for key, meta in sensor_meta.items():
            if key in EXCLUDE:
                continue
            card = SensorCard(key, meta, parent=self)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._cards[key] = card
            # Don't add to layout yet — added on first reveal

    # ── Public API ────────────────────────────────────────────────────────────

    def update_sensor(
        self,
        key:           str,
        value:         float | None,
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

        if not was_visible and card.isVisible():
            if key not in self._arrival_order:
                self._arrival_order.append(key)
                self._relayout()

    def flash_alarm_cards(self) -> None:
        for card in self._cards.values():
            card.flash_toggle()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _relayout(self) -> None:
        """Re-assign grid positions based on arrival order."""
        # Remove everything from layout without deleting widgets
        while self._layout.count():
            item = self._layout.takeAt(0)
            # takeAt removes from layout; widget stays alive

        rows = (len(self._arrival_order) + COLS - 1) // COLS
        for row in range(max(rows, 1)):
            self._layout.setRowStretch(row, 1)

        for idx, key in enumerate(self._arrival_order):
            row = idx // COLS
            col = idx % COLS
            card = self._cards[key]
            self._layout.addWidget(card, row, col)

        log.debug("Grid relayout: %d cards visible", len(self._arrival_order))
