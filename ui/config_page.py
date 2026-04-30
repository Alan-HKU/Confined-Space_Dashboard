"""
config_page.py — Password-protected configuration page.
"""

import ast
import configparser
import logging
from pathlib import Path

from PySide6.QtCore    import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QGridLayout,
    QDialog, QStackedWidget, QSizePolicy
)

from core.config   import get, get_sensor
from core.app_paths import CONFIG_PATH
from ui.styles   import (C_BG_PANEL, C_BG_SIDEBAR, C_BG_CARD,
                          C_BORDER, C_BORDER_MID,
                          C_TEXT_PRI, C_TEXT_SEC, C_ACCENT, C_ALARM,
                          C_TEXT_DIM, C_NORMAL, C_WARN)
log = logging.getLogger(__name__)
# CONFIG_PATH is now resolved correctly for both dev and frozen exe


# ── Custom message dialog (replaces QMessageBox) ──────────────────────────────

class _MsgDialog(QDialog):
    """
    Minimal dark-theme modal dialog.
    kind: "info" | "error"
    """

    def __init__(self, title: str, message: str, kind: str = "info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setMinimumWidth(360)

        # ── Outer frame with border ──────────────────────────────────────────
        self.setStyleSheet(
            f"QDialog {{"
            f"  background-color: {C_BG_SIDEBAR};"
            f"  border: 1px solid {C_BORDER_MID};"
            f"  border-radius: 10px;"
            f"}}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Title bar strip ──────────────────────────────────────────────────
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        accent = C_ACCENT if kind == "info" else C_ALARM
        title_bar.setStyleSheet(
            f"QFrame {{"
            f"  background-color: {C_BG_PANEL};"
            f"  border-bottom: 2px solid {accent};"
            f"  border-top-left-radius: 10px;"
            f"  border-top-right-radius: 10px;"
            f"}}"
        )
        tb_lay = QHBoxLayout(title_bar)
        tb_lay.setContentsMargins(16, 0, 16, 0)

        icon_map = {"info": "✅", "error": "❌"}
        icon_lbl = QLabel(icon_map.get(kind, "ℹ"))
        icon_lbl.setStyleSheet(
            "font-size: 13pt; background: transparent; border: none;"
        )
        tb_lay.addWidget(icon_lbl)
        tb_lay.addSpacing(8)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: 11pt; font-weight: bold; color: {C_TEXT_PRI};"
            " background: transparent; border: none;"
        )
        tb_lay.addWidget(title_lbl)
        tb_lay.addStretch(1)

        root.addWidget(title_bar)

        # ── Message body ─────────────────────────────────────────────────────
        body = QFrame()
        body.setStyleSheet(
            f"QFrame {{ background-color: {C_BG_SIDEBAR}; border: none; }}"
        )
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 20, 24, 8)
        body_lay.setSpacing(20)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            f"font-size: 10pt; color: {C_TEXT_PRI}; line-height: 160%;"
            " background: transparent; border: none;"
        )
        msg_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        body_lay.addWidget(msg_lbl)

        # ── OK button ────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton("確認")
        ok_btn.setObjectName("btn_primary")
        ok_btn.setFixedHeight(34)
        ok_btn.setMinimumWidth(90)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        body_lay.addLayout(btn_row)
        body_lay.addSpacing(4)

        root.addWidget(body)

    @classmethod
    def info(cls, parent, title: str, message: str):
        cls(title, message, kind="info",  parent=parent).exec()

    @classmethod
    def error(cls, parent, title: str, message: str):
        cls(title, message, kind="error", parent=parent).exec()


# ── Field definitions ─────────────────────────────────────────────────────────

_GENERAL_FIELDS = [
    ("station_ID",         "站點 ID"),
    ("device_ID",          "設備 ID"),
    ("location",           "位置描述"),
    ("GUIReflashTime",     "GUI 刷新間隔 (ms)"),
    ("LoggingTime",        "CSV 日誌間隔 (ms)"),
    ("DataReflashTime",    "數據刷新間隔 (ms)"),
    ("MQTTTime",           "MQTT 上行間隔 (ms)"),
    ("sensor_upload_interval", "傳感器數據上傳間隔 (s)"),
    ("DisplaySwitchTime",  "頁面輪換間隔 (ms)"),
    ("ConnectionTimeOut",  "連接超時 (s)"),
    ("AlarmTimeOut",       "報警超時 (s)"),
    ("DPI",                "DPI 縮放"),
    ("card_name_font_size",  "卡片名稱字體大小 (pt)"),
    ("card_value_font_size", "卡片數值字體大小 (pt)"),
    ("card_unit_font_size",  "卡片單位字體大小 (pt)"),
    ("audio_playing",      "啟用報警音頻 (True/False)"),
    ("alarm_sound_file",   "報警音頻文件"),
    ("alarm_border_flash", "啟用邊框閃爍 (True/False)"),
    ("LogLocation",        "CSV 日誌文件路徑"),
    ("log_max_bytes",      "最大日誌文件大小 (bytes)"),
    ("log_backup_count",   "最多備份日誌數量"),
    ("log_file_level",     "日誌文件記錄級別 (DEBUG/INFO/WARNING)"),
    ("battery_check_interval", "本機電池輪詢間隔 (s)"),
]

_CONNECTION_FIELDS = [
    ("private_broker",       "本地 Broker 地址"),
    ("private_broker_port",  "本地 Broker 端口"),
    ("private_topic",        "本地訂閱主題"),
    ("public_broker",        "網絡 Broker 地址"),
    ("public_broker_port",   "網絡 Broker 端口"),
    ("ping_ip",              "Ping 測試 IP"),
]

# Note: public topic prefix is auto-computed as cs/<site_name>/<gateway_id>
# Edit site_name and gateway_id in GENERAL section above.

_SECTION_MAP: dict[str, str] = {}
for _k, _ in _GENERAL_FIELDS:    _SECTION_MAP[_k] = "GENERAL"
for _k, _ in _CONNECTION_FIELDS: _SECTION_MAP[_k] = "CONNECTION"
_SECTION_MAP["config_password"] = "GENERAL"


# ── Toggle button (ON/OFF switch) ─────────────────────────────────────────────

_TOGGLE_ON_QSS = (
    "QPushButton {"
    f"  background-color: {C_NORMAL};"
    "  color: #1a1d23;"
    "  border: none;"
    "  border-radius: 11px;"
    "  font-size: 8pt;"
    "  font-weight: bold;"
    "  padding: 2px 10px;"
    "  min-width: 52px;"
    "  min-height: 22px;"
    "}"
    "QPushButton:hover { background-color: #6fffab; }"
)

_TOGGLE_OFF_QSS = (
    "QPushButton {"
    f"  background-color: {C_BORDER_MID};"
    f"  color: {C_TEXT_DIM};"
    "  border: none;"
    "  border-radius: 11px;"
    "  font-size: 8pt;"
    "  font-weight: bold;"
    "  padding: 2px 10px;"
    "  min-width: 52px;"
    "  min-height: 22px;"
    "}"
    "QPushButton:hover {"
    f"  background-color: {C_BORDER}; color: {C_TEXT_SEC};"
    "}"
)


class _ToggleBtn(QPushButton):
    """Simple ON/OFF toggle button."""

    def __init__(self, initial: bool = True, parent=None):
        super().__init__(parent)
        self._state = initial
        self.setCheckable(False)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._toggle)
        self._refresh()

    def _toggle(self):
        self._state = not self._state
        self._refresh()

    def _refresh(self):
        self.setText("啟用" if self._state else "關閉")
        self.setStyleSheet(_TOGGLE_ON_QSS if self._state else _TOGGLE_OFF_QSS)

    def value(self) -> bool:
        return self._state

    def set_value(self, v: bool):
        self._state = bool(v)
        self._refresh()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _raw_value(section: str, key: str) -> str:
    cfg = configparser.RawConfigParser()
    cfg.read(CONFIG_PATH, encoding="utf-8")
    try:
        v = cfg.get(section, key).strip()
        if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
            v = v[1:-1]
        return v
    except (configparser.NoSectionError, configparser.NoOptionError):
        return ""


# ── Password overlay ──────────────────────────────────────────────────────────

class _PasswordOverlay(QWidget):
    authenticated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("pwd_card")
        card.setFixedWidth(380)

        cly = QVBoxLayout(card)
        cly.setContentsMargins(36, 32, 36, 32)
        cly.setSpacing(14)

        icon = QLabel("🔒")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 30pt; background: transparent; border: none;")
        cly.addWidget(icon)

        title = QLabel("配置頁面")
        title.setObjectName("pwd_title")
        title.setAlignment(Qt.AlignCenter)
        cly.addWidget(title)

        hint = QLabel("請輸入管理密碼繼續")
        hint.setObjectName("pwd_hint")
        hint.setAlignment(Qt.AlignCenter)
        cly.addWidget(hint)

        cly.addSpacing(4)

        self._inp = QLineEdit()
        self._inp.setEchoMode(QLineEdit.Password)
        self._inp.setPlaceholderText("密碼")
        self._inp.setFixedHeight(36)
        self._inp.returnPressed.connect(self._check)
        cly.addWidget(self._inp)

        self._err = QLabel("")
        self._err.setObjectName("pwd_error")
        self._err.setAlignment(Qt.AlignCenter)
        self._err.setFixedHeight(18)
        cly.addWidget(self._err)

        cly.addSpacing(4)

        btn = QPushButton("確認進入")
        btn.setObjectName("btn_primary")
        btn.setFixedHeight(36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._check)
        cly.addWidget(btn)

        outer.addWidget(card)

    def reset(self):
        self._inp.clear()
        self._err.setText("")

    def _check(self):
        entered  = self._inp.text()
        expected = str(get("config_password") or "1234")
        if entered == expected:
            self.authenticated.emit()
        else:
            self._err.setText("密碼錯誤，請重試")
            self._inp.selectAll()
            self._inp.setFocus()


# ── Config form ───────────────────────────────────────────────────────────────

class _ConfigForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fields:  dict[str, QLineEdit]  = {}
        self._toggles: dict[str, _ToggleBtn] = {}
        self._topic_preview: QLineEdit = QLineEdit()   # placeholder, replaced in _add_section

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("cfg_form_content")
        self._form_lay = QVBoxLayout(content)
        self._form_lay.setContentsMargins(28, 16, 28, 16)
        self._form_lay.setSpacing(4)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # Action bar
        bar = QFrame()
        bar.setObjectName("cfg_action_bar")
        bar.setFixedHeight(52)
        bly = QHBoxLayout(bar)
        bly.setContentsMargins(20, 8, 20, 8)
        bly.setSpacing(10)

        self._btn_lock = QPushButton("🔒  鎖定配置")
        self._btn_lock.setObjectName("btn_secondary")
        self._btn_lock.setFixedHeight(34)
        self._btn_lock.setCursor(Qt.PointingHandCursor)

        self._btn_save = QPushButton("💾  保存設置")
        self._btn_save.setObjectName("btn_primary")
        self._btn_save.setFixedHeight(34)
        self._btn_save.setMinimumWidth(120)
        self._btn_save.setCursor(Qt.PointingHandCursor)

        bly.addWidget(self._btn_lock)
        bly.addStretch(1)
        bly.addWidget(self._btn_save)
        root.addWidget(bar)

        # Build form sections
        self._add_section("GENERAL",    "通用設置",  _GENERAL_FIELDS)
        self._add_section("CONNECTION", "連接設置",  _CONNECTION_FIELDS)
        self._add_alarm_section()
        self._add_password_section()
        self._form_lay.addStretch(1)

    # ── Section builders ──────────────────────────────────────────────────────

    def _section_header(self, title: str):
        self._form_lay.addSpacing(10)
        hdr = QLabel(f"▸  {title}")
        hdr.setObjectName("cfg_section_label")
        self._form_lay.addWidget(hdr)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {C_BORDER}; border: none;")
        self._form_lay.addWidget(sep)
        self._form_lay.addSpacing(4)

    def _add_section(self, cfg_sec: str, heading: str, fields: list):
        self._section_header(heading)
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)

        for row, (key, label) in enumerate(fields):
            lbl = QLabel(label)
            lbl.setObjectName("cfg_key_label")
            lbl.setFixedWidth(200)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            inp = QLineEdit(_raw_value(cfg_sec, key))
            inp.setFixedHeight(28)
            inp.setToolTip(f"[{cfg_sec}]  {key}")

            grid.addWidget(lbl, row, 0)
            grid.addWidget(inp, row, 1)
            self._fields[key] = inp

        # For CONNECTION section: append auto-computed topic prefix row
        if cfg_sec == "CONNECTION":
            row = len(fields)
            hint_lbl = QLabel("網絡上傳主題（自動）")
            hint_lbl.setObjectName("cfg_key_label")
            hint_lbl.setFixedWidth(200)
            hint_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self._topic_preview = QLineEdit()
            self._topic_preview.setFixedHeight(28)
            self._topic_preview.setReadOnly(True)
            self._topic_preview.setToolTip(
                "自動由 site_name / gateway_id 組合，無需手動填寫\n"
                "格式: cs/<site_name>/<gateway_id>/(bind|sensor|heartbeat)"
            )
            self._topic_preview.setStyleSheet(
                f"color: {C_TEXT_DIM}; background-color: {C_BG_CARD};"
                f" border: 1px solid {C_BORDER}; border-radius: 5px; padding: 4px 8px;"
            )
            self._update_topic_preview()

            # Update preview whenever site_name or gateway_id changes
            if "site_name" in self._fields:
                self._fields["site_name"].textChanged.connect(
                    lambda _: self._update_topic_preview())
            if "gateway_id" in self._fields:
                self._fields["gateway_id"].textChanged.connect(
                    lambda _: self._update_topic_preview())

            grid.addWidget(hint_lbl,           row, 0)
            grid.addWidget(self._topic_preview, row, 1)

        self._form_lay.addLayout(grid)

    def _update_topic_preview(self):
        site = (self._fields.get("site_name") or QLineEdit()).text().strip() or "site_001"
        gw   = (self._fields.get("gateway_id") or QLineEdit()).text().strip() or "GW_01"
        self._topic_preview.setText(f"cs/{site}/{gw}/(bind | sensor | heartbeat)")

    def _add_alarm_section(self):
        """Per-sensor alarm enable/disable toggles."""
        self._section_header("報警設置  （關閉後不播放聲音，但仍顯示顏色）")

        sensor_meta = get_sensor()
        # Read current alarm_enabled list from config
        raw_enabled = _raw_value("SENSOR", "alarm_enabled")
        try:
            enabled_list: list = ast.literal_eval(raw_enabled) if raw_enabled else []
        except (ValueError, SyntaxError):
            enabled_list = []

        # Build key→enabled map
        sensor_keys = [k for k in sensor_meta.keys() if k != "cam"]
        enabled_map: dict[str, bool] = {}
        for i, key in enumerate(sensor_meta.keys()):
            enabled_map[key] = bool(enabled_list[i]) if i < len(enabled_list) else True

        # Grid: 3 columns of (name, toggle) pairs
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)
        COLS = 3  # pairs per row

        for idx, key in enumerate(sensor_keys):
            meta = sensor_meta[key]
            row  = idx // COLS
            col  = (idx % COLS) * 2

            name_lbl = QLabel(meta.get("name", key))
            name_lbl.setObjectName("cfg_key_label")
            name_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            name_lbl.setFixedWidth(120)

            toggle = _ToggleBtn(initial=enabled_map.get(key, True))
            self._toggles[key] = toggle

            grid.addWidget(name_lbl, row, col)
            grid.addWidget(toggle,   row, col + 1)

        self._form_lay.addLayout(grid)

    def _add_password_section(self):
        self._section_header("密碼管理")
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)

        lbl = QLabel("配置頁密碼")
        lbl.setObjectName("cfg_key_label")
        lbl.setFixedWidth(200)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        inp = QLineEdit()
        inp.setEchoMode(QLineEdit.Password)
        inp.setFixedHeight(28)
        inp.setPlaceholderText("留空保持不變")
        inp.setToolTip("[GENERAL]  config_password")

        grid.addWidget(lbl, 0, 0)
        grid.addWidget(inp, 0, 1)
        self._fields["config_password"] = inp
        self._form_lay.addLayout(grid)

    # ── Save ──────────────────────────────────────────────────────────────────

    def save(self) -> bool:
        cfg = configparser.RawConfigParser()
        cfg.read(CONFIG_PATH, encoding="utf-8")

        changed = False

        # ── Text fields ──
        for key, inp in self._fields.items():
            val = inp.text().strip()
            if not val:
                continue
            sec = _SECTION_MAP.get(key, "GENERAL")
            if not cfg.has_section(sec):
                cfg.add_section(sec)
            old = cfg.get(sec, key, fallback=None)
            new_raw = f'"{val}"' if (old and old.strip().startswith('"')) else val
            if old != new_raw:
                cfg.set(sec, key, new_raw)
                changed = True

        # ── Alarm toggles → write alarm_enabled list ──
        if self._toggles:
            sensor_keys_all = list(get_sensor().keys())  # includes cam
            # Build new list preserving order from config
            new_enabled = []
            for key in sensor_keys_all:
                if key in self._toggles:
                    new_enabled.append(self._toggles[key].value())
                else:
                    # cam or any key without toggle — keep existing or True
                    raw = _raw_value("SENSOR", "alarm_enabled")
                    try:
                        old_list = ast.literal_eval(raw) if raw else []
                    except (ValueError, SyntaxError):
                        old_list = []
                    idx = sensor_keys_all.index(key)
                    new_enabled.append(bool(old_list[idx]) if idx < len(old_list) else True)

            new_raw = str(new_enabled)
            if not cfg.has_section("SENSOR"):
                cfg.add_section("SENSOR")
            old_raw = cfg.get("SENSOR", "alarm_enabled", fallback=None)
            if old_raw != new_raw:
                cfg.set("SENSOR", "alarm_enabled", new_raw)
                changed = True

        if not changed:
            return True

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                cfg.write(f)
            log.info("config.ini saved")
            return True
        except OSError as exc:
            log.error("Failed to save config.ini: %s", exc)
            return False

    def reload(self):
        """Reload all fields and toggles from disk."""
        for sec, fields in [("GENERAL", _GENERAL_FIELDS), ("CONNECTION", _CONNECTION_FIELDS)]:
            for key, _ in fields:
                if key in self._fields:
                    self._fields[key].setText(_raw_value(sec, key))

        if "config_password" in self._fields:
            self._fields["config_password"].setText("")

        # Reload alarm toggles
        raw = _raw_value("SENSOR", "alarm_enabled")
        try:
            enabled_list = ast.literal_eval(raw) if raw else []
        except (ValueError, SyntaxError):
            enabled_list = []

        sensor_keys_all = list(get_sensor().keys())
        for i, key in enumerate(sensor_keys_all):
            if key in self._toggles:
                val = bool(enabled_list[i]) if i < len(enabled_list) else True
                self._toggles[key].set_value(val)

    @property
    def btn_save(self): return self._btn_save

    @property
    def btn_lock(self): return self._btn_lock


# ── ConfigPage (public) ───────────────────────────────────────────────────────

class ConfigPage(QWidget):
    locked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stack   = QStackedWidget(self)
        self._overlay = _PasswordOverlay()
        self._form    = _ConfigForm()
        self._stack.addWidget(self._overlay)
        self._stack.addWidget(self._form)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._stack)

        self._overlay.authenticated.connect(self._on_auth)
        self._form.btn_save.clicked.connect(self._on_save)
        self._form.btn_lock.clicked.connect(self._on_lock)
        self._stack.setCurrentIndex(0)

    def _on_auth(self):
        self._form.reload()
        self._stack.setCurrentIndex(1)

    def _on_save(self):
        ok = self._form.save()
        if ok:
            _MsgDialog.info(
                self,
                "保存成功",
                "設置已保存至 config.ini\n\n部分設置需要重啓程序後才能生效。"
            )
        else:
            _MsgDialog.error(
                self,
                "保存失敗",
                "無法寫入 config.ini\n請檢查文件是否存在或權限是否正確。"
            )

    def _on_lock(self):
        self._stack.setCurrentIndex(0)
        self._overlay.reset()
        self.locked.emit()

    def lock(self):
        self._stack.setCurrentIndex(0)
        self._overlay.reset()
