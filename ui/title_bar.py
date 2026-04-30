"""
title_bar.py — Frameless custom title bar with drag-to-move support.

Provides: hamburger | logo | title | min / max / close
"""

from pathlib import Path

from PySide6.QtCore    import Qt, QPoint, Signal
from PySide6.QtGui     import QMouseEvent, QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy

from ui.styles import C_TITLE_BAR, C_TEXT_SEC, C_BORDER

_ASSETS = Path(__file__).parent.parent / "assets"
_BAR_H  = 40
_LOGO_H = 26


class TitleBar(QWidget):
    sidebar_toggle_requested = Signal()

    def __init__(self, window: QWidget, title: str = "", parent=None):
        super().__init__(parent)
        self._window    = window
        self._drag_pos  = QPoint()
        self._maximized = False

        self.setObjectName("title_bar")
        self.setFixedHeight(_BAR_H)
        self.setStyleSheet(
            f"#title_bar {{ background-color: {C_TITLE_BAR};"
            f" border-bottom: 1px solid {C_BORDER}; }}"
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 0, 0, 0)
        lay.setSpacing(0)

        # Hamburger
        self._btn_toggle = QPushButton("☰")
        self._btn_toggle.setObjectName("sidebar_toggle")
        self._btn_toggle.setFixedSize(_BAR_H, _BAR_H)
        self._btn_toggle.setFlat(True)
        self._btn_toggle.setCursor(Qt.PointingHandCursor)
        self._btn_toggle.setToolTip("展開 / 收縮側欄")
        self._btn_toggle.clicked.connect(self.sidebar_toggle_requested)
        lay.addWidget(self._btn_toggle)

        lay.addSpacing(4)

        # Logo
        self._logo_lbl = QLabel()
        self._logo_lbl.setObjectName("title_logo")
        self._logo_lbl.setStyleSheet("background: transparent; border: none;")
        self._logo_lbl.setFixedSize(_LOGO_H, _LOGO_H)
        self._logo_lbl.setAlignment(Qt.AlignCenter)
        self._load_logo()
        lay.addWidget(self._logo_lbl)

        lay.addSpacing(8)

        # Title
        self._lbl_title = QLabel(title)
        self._lbl_title.setObjectName("title_label")
        self._lbl_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self._lbl_title)

        # Window buttons
        self._btn_min   = self._make_btn("─", "最小化", self._on_minimize)
        self._btn_max   = self._make_btn("□", "最大化", self._on_maximize)
        self._btn_close = self._make_btn("✕", "關閉",   self._on_close, close=True)
        lay.addWidget(self._btn_min)
        lay.addWidget(self._btn_max)
        lay.addWidget(self._btn_close)

    def _load_logo(self):
        from core.app_paths import resolve_asset
        p = resolve_asset("Picture1.png")
        if p.exists():
            px = QPixmap(str(p)).scaledToHeight(_LOGO_H, Qt.SmoothTransformation)
            self._logo_lbl.setPixmap(px)
        else:
            self._logo_lbl.setText("⬡")
            self._logo_lbl.setStyleSheet(
                "color: #bd93f9; font-size: 16pt; background: transparent; border: none;"
            )

    def _make_btn(self, text, tip, slot, *, close=False) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("wintitle_btn_close" if close else "wintitle_btn")
        btn.setFixedSize(_BAR_H, _BAR_H)
        btn.setFlat(True)
        btn.setToolTip(tip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def _on_minimize(self): self._window.showMinimized()

    def _on_maximize(self):
        if self._maximized:
            self._window.showNormal()
            self._btn_max.setText("□")
            self._maximized = False
        else:
            self._window.showMaximized()
            self._btn_max.setText("❐")
            self._maximized = True

    def _on_close(self): self._window.close()

    def set_title(self, t: str): self._lbl_title.setText(t)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and not self._drag_pos.isNull():
            if self._maximized:
                self._on_maximize()
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._window.move(self._window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._on_maximize()
