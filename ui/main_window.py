"""
main_window.py — MainWindow: frameless dark-theme shell.

Layout
------
  ┌──────── title_bar (hamburger | title | min/max/close) ────────────┐
  │ sidebar │                 stacked pages                            │
  │ [icon]  │   ┌── home (sensor grid) ──────────────────────────┐   │
  │ [icon]  │   │  6×2 sensor cards (hidden until data arrives)  │   │
  │         │   └────────────────────────────────────────────────┘   │
  ├─────────┴───────── status_bar ────────────────────────────────────┤
  └───────────────────────────────────────────────────────────────────┘

Sidebar collapses to icon-only (48px) / expands to 160px via animation.
"""

import logging
from datetime import datetime

from PySide6.QtCore    import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QSizePolicy,
    QSizeGrip, QApplication
)

from core.config     import get, get_sensor
from core.data_model import DataModel, get_mqtt_status
from ui.styles       import (MAIN_QSS, C_BG_SIDEBAR, C_BORDER, C_ACCENT,
                              C_TEXT_SEC, C_TEXT_PRI, C_BG_PANEL)
from ui.title_bar    import TitleBar
from ui.status_bar   import StatusBar
from ui.sensor_grid  import SensorGrid
from ui.config_page  import ConfigPage
from ui.alarm_controller import AlarmController

log = logging.getLogger(__name__)

_SIDEBAR_COLLAPSED = 52
_SIDEBAR_EXPANDED  = 164
_ANIM_MS           = 220


# ── Nav button ────────────────────────────────────────────────────────────────

class _NavBtn(QPushButton):
    """Sidebar navigation button with icon + optional text."""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._text = text
        self.setObjectName("nav_btn")
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._set_expanded(True)

    def set_expanded(self, expanded: bool):
        self._set_expanded(expanded)

    def _set_expanded(self, expanded: bool):
        if expanded:
            self.setText(f"  {self._icon}  {self._text}")
            self.setToolTip("")
            self.setStyleSheet("")          # back to QSS
        else:
            self.setText(self._icon)        # icon only, centred
            self.setToolTip(self._text)
            # Force center alignment when icon-only
            self.setStyleSheet(
                "QPushButton#nav_btn { text-align: center; padding: 10px 4px; font-size: 16pt; }"
                "QPushButton#nav_btn:hover { background-color: rgba(255,255,255,0.06);"
                " border-left: 3px solid #4a5060; }"
                "QPushButton#nav_btn:checked { background-color: rgba(189,147,249,0.12);"
                " border-left: 3px solid #bd93f9; }"
            )


# ── MainWindow ────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self, data_model: DataModel):
        super().__init__()
        self._data        = data_model
        self._alarm_ctrl  = AlarmController()
        self._sensor_meta = get_sensor()
        self._sidebar_expanded = False          # ← 預設收起

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1280, 760)
        self.setMinimumSize(QSize(940, 560))
        self.setWindowTitle("密閉空間監測系統")
        self.setStyleSheet(MAIN_QSS)
        self._build_shell()
        self._build_pages()
        self._wire_nav()
        self._init_timers()

        self._nav_home.setChecked(True)
        self._pages.setCurrentIndex(0)

    # ── Root shell ────────────────────────────────────────────────────────────

    def _build_shell(self):
        # Outer container — provides rounded border
        self._root = QWidget()
        self._root.setObjectName("root_widget")
        self._root.setStyleSheet(
            "#root_widget {"
            f"  background-color: {C_BG_PANEL};"
            f"  border: 1px solid {C_BORDER};"
            "  border-radius: 10px;"
            "}"
        )
        self.setCentralWidget(self._root)

        root_lay = QVBoxLayout(self._root)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # ── Title bar ──
        self._title_bar = TitleBar(self, title="密閉空間監測系統", parent=self._root)
        self._title_bar.sidebar_toggle_requested.connect(self._toggle_sidebar)
        root_lay.addWidget(self._title_bar)

        # ── Middle (sidebar + pages) ──
        mid = QWidget()
        mid.setStyleSheet("background: transparent;")
        mid_lay = QHBoxLayout(mid)
        mid_lay.setContentsMargins(0, 0, 0, 0)
        mid_lay.setSpacing(0)

        # ── Sidebar ──
        self._sidebar = QFrame()
        self._sidebar.setObjectName("sidebar")
        self._sidebar.setFixedWidth(_SIDEBAR_COLLAPSED)     # ← 預設收起寬度
        self._sidebar.setStyleSheet(
            f"#sidebar {{ background-color: {C_BG_SIDEBAR};"
            f" border-right: 1px solid {C_BORDER}; }}"
        )
        sb_lay = QVBoxLayout(self._sidebar)
        sb_lay.setContentsMargins(0, 6, 0, 6)
        sb_lay.setSpacing(2)

        self._nav_home   = _NavBtn("🌐", "主頁")
        self._nav_config = _NavBtn("🔨", "配置")
        sb_lay.addWidget(self._nav_home)
        sb_lay.addWidget(self._nav_config)
        sb_lay.addStretch(1)

        self._nav_btns = [self._nav_home, self._nav_config]

        # 初始化按鈕為收起狀態
        for btn in self._nav_btns:
            btn.set_expanded(False)

        # ── Pages ──
        self._pages = QStackedWidget()
        self._pages.setStyleSheet("background: transparent;")

        mid_lay.addWidget(self._sidebar)
        mid_lay.addWidget(self._pages, 1)

        root_lay.addWidget(mid, 1)

        # ── Status bar ──
        self._status_bar = StatusBar(self._root)
        root_lay.addWidget(self._status_bar)

        # ── Size grip (anchored inside root, bottom-right) ──
        self._grip = QSizeGrip(self._root)
        self._grip.setFixedSize(14, 14)
        self._grip.setStyleSheet("background: transparent;")
        # Positioned in resizeEvent

    # ── Pages ─────────────────────────────────────────────────────────────────

    def _build_pages(self):
        self._grid    = SensorGrid(self._sensor_meta, parent=self)
        self._cfg_page = ConfigPage(parent=self)

        self._pages.addWidget(self._grid)     # 0 — home
        self._pages.addWidget(self._cfg_page) # 1 — config

    def _wire_nav(self):
        self._nav_home.clicked.connect(self._go_home)
        self._nav_config.clicked.connect(self._go_config)
        self._cfg_page.locked.connect(self._go_home)

    def _go_home(self):
        self._pages.setCurrentIndex(0)
        self._nav_home.setChecked(True)

    def _go_config(self):
        self._pages.setCurrentIndex(1)
        self._nav_config.setChecked(True)

    # ── Sidebar animation ─────────────────────────────────────────────────────

    def _toggle_sidebar(self):
        self._sidebar_expanded = not self._sidebar_expanded
        target = _SIDEBAR_EXPANDED if self._sidebar_expanded else _SIDEBAR_COLLAPSED

        self._anim = QPropertyAnimation(self._sidebar, b"minimumWidth")
        self._anim.setDuration(_ANIM_MS)
        self._anim.setStartValue(self._sidebar.width())
        self._anim.setEndValue(target)
        self._anim.setEasingCurve(QEasingCurve.InOutQuart)

        self._anim2 = QPropertyAnimation(self._sidebar, b"maximumWidth")
        self._anim2.setDuration(_ANIM_MS)
        self._anim2.setStartValue(self._sidebar.width())
        self._anim2.setEndValue(target)
        self._anim2.setEasingCurve(QEasingCurve.InOutQuart)

        self._anim.start()
        self._anim2.start()

        for btn in self._nav_btns:
            btn.set_expanded(self._sidebar_expanded)

    # ── Timers ────────────────────────────────────────────────────────────────

    def _init_timers(self):
        t_gui = QTimer(self)
        t_gui.timeout.connect(self._on_gui_tick)
        t_gui.start(get("GUIReflashTime") or 1000)

        t_data = QTimer(self)
        t_data.timeout.connect(self._data.get)
        t_data.start(get("DataReflashTime") or 2000)

        t_log = QTimer(self)
        t_log.timeout.connect(self._data.log)
        t_log.start(get("LoggingTime") or 30000)

    # ── GUI tick ──────────────────────────────────────────────────────────────

    def _on_gui_tick(self):
        # Drain MQTT buffer first — instant bind/unbind response
        self._data.get()

        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self._status_bar.set_clock(now)
        self._status_bar.set_private_mqtt(get_mqtt_status("private"))
        self._status_bar.set_public_mqtt(get_mqtt_status("public"))

        # Bind state driven by explicit MQTT {"status":"bind"/"unbind"} message
        bound = self._data.is_bound()
        self._status_bar.set_bind_status(bound)

        # Alarm: only when bound AND at least one LIVE sensor exceeds LV2
        # Error/Offline sensors are NOT alarm conditions
        lv2_alarm = bound and self._data.any_alarm()
        flash = self._alarm_ctrl.tick(lv2_alarm)

        for key in self._data.sensor_keys():
            s_state    = self._data.sensor_state(key)
            level      = self._data.alarm_level(key)
            value      = self._data.reading(key)
            dev_id     = self._data.device_id(key)
            stale      = s_state in ("offline", "waiting")
            card_flash = flash and (level == "alarm") and s_state == "live"
            self._grid.update_sensor(
                key, value, dev_id, level, stale,
                flash=card_flash,
                has_timestamp=self._data.has_timestamp(key),
                sensor_state=s_state,
            )

        self._status_bar.update_device_batteries(self._data.get_device_batteries())
        self._status_bar.update_local_battery()

    # ── Qt events ─────────────────────────────────────────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep size grip pinned to bottom-right of root widget
        rw = self._root.width()
        rh = self._root.height()
        self._grip.move(rw - self._grip.width() - 2,
                        rh - self._grip.height() - 2)

    def closeEvent(self, event):
        self._alarm_ctrl.stop()
        super().closeEvent(event)

