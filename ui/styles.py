"""
styles.py — Single source of truth for all colours and QSS.

Qt QSS selector rules (differs from CSS!):
  #name              → matches objectName="name" on ANY widget type
  ClassName          → matches by C++ class name (QPushButton, QLabel ...)
  ClassName[objectName="x"] → type + objectName combined (most precise)

NEVER use:  QPushButton#name  ← CSS syntax, Qt does NOT support it
NEVER use:  box-sizing        ← CSS property, Qt does NOT support it
"""

import sys as _sys

# ── Platform-aware font stack ─────────────────────────────────────────────────
# Windows : Segoe UI  (system UI) + Microsoft JhengHei / YaHei (CJK)
# Linux   : Noto Sans (Ubuntu/Debian) + WenQuanYi / Noto Sans CJK
if _sys.platform == "win32":
    _FONT_FAMILY = '"Segoe UI", "Microsoft JhengHei", "Microsoft YaHei", sans-serif'
else:
    _FONT_FAMILY = '"Noto Sans", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans", sans-serif'


C_BG_DEEP    = "#1a1d23"
C_BG_PANEL   = "#282c34"
C_BG_SIDEBAR = "#21252b"
C_BG_CARD    = "#2c313a"
C_BG_INPUT   = "#1e2127"
C_BORDER     = "#373c47"
C_BORDER_MID = "#4a5060"
C_TEXT_PRI   = "#dcdcdc"
C_TEXT_SEC   = "#7a8494"
C_TEXT_DIM   = "#4e5566"
C_ACCENT     = "#bd93f9"
C_ACCENT2    = "#8be9fd"
C_NORMAL     = "#50fa7b"
C_WARN       = "#f1fa8c"
C_ALARM      = "#ff5555"
C_TITLE_BAR  = "#21252b"

MAIN_QSS = f"""
/* ═══════════════════════════════════════════
   GLOBAL BASE
   ═══════════════════════════════════════════ */
QWidget {{
    background-color: {C_BG_PANEL};
    color: {C_TEXT_PRI};
    font-family: {_FONT_FAMILY};
    font-size: 10pt;
}}

QToolTip {{
    color: #ffffff;
    background-color: {C_BG_SIDEBAR};
    border: 1px solid {C_BORDER_MID};
    border-left: 3px solid {C_ACCENT};
    padding: 4px 10px;
    border-radius: 4px;
}}

/* ═══════════════════════════════════════════
   TITLE BAR
   ═══════════════════════════════════════════ */
#title_bar {{
    background-color: {C_TITLE_BAR};
    border-bottom: 1px solid {C_BORDER};
}}
#title_bar QLabel {{
    background: transparent;
    border: none;
}}
#title_label {{
    color: {C_TEXT_PRI};
    font-size: 12pt;
    font-weight: bold;
    padding-left: 2px;
    background: transparent;
    border: none;
}}
#sidebar_toggle {{
    background-color: transparent;
    color: {C_TEXT_SEC};
    font-size: 15pt;
    border: none;
    border-radius: 5px;
    padding: 2px;
}}
#sidebar_toggle:hover {{
    background-color: rgba(255,255,255,0.07);
    color: {C_TEXT_PRI};
}}
#wintitle_btn {{
    background-color: transparent;
    color: {C_TEXT_SEC};
    font-size: 11pt;
    border: none;
}}
#wintitle_btn:hover {{
    background-color: rgba(255,255,255,0.08);
    color: {C_TEXT_PRI};
}}
#wintitle_btn_close {{
    background-color: transparent;
    color: {C_TEXT_SEC};
    font-size: 11pt;
    border: none;
}}
#wintitle_btn_close:hover {{
    background-color: #c0392b;
    color: #ffffff;
}}

/* ═══════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════ */
#sidebar {{
    background-color: {C_BG_SIDEBAR};
    border-right: 1px solid {C_BORDER};
    border-top: none;
    border-bottom: none;
    border-left: none;
}}
#nav_btn {{
    background-color: transparent;
    color: {C_TEXT_SEC};
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 10px 14px;
    font-size: 10pt;
    border-radius: 0px;
}}
#nav_btn:hover {{
    background-color: rgba(255,255,255,0.04);
    color: {C_TEXT_PRI};
    border-left: 3px solid {C_BORDER_MID};
}}
#nav_btn:checked {{
    background-color: rgba(189,147,249,0.10);
    color: {C_ACCENT};
    border-left: 3px solid {C_ACCENT};
    font-weight: bold;
}}

/* ═══════════════════════════════════════════
   STATUS BAR
   ═══════════════════════════════════════════ */
#status_bar {{
    background-color: {C_BG_SIDEBAR};
    border-top: 1px solid {C_BORDER};
    border-bottom: none;
    border-left: none;
    border-right: none;
}}
#status_bar QLabel {{
    background: transparent;
    border: none;
}}

/* ═══════════════════════════════════════════
   SENSOR CARD
   ═══════════════════════════════════════════ */
#sensor_card {{
    background-color: {C_BG_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
}}
#sensor_card QLabel {{
    background: transparent;
    border: none;
}}
#card_name   {{ color: {C_TEXT_PRI}; font-size: 9pt; font-weight: 600; background: transparent; border: none; }}
#card_device {{ color: {C_TEXT_DIM}; font-size: 8pt; background: transparent; border: none; }}
#card_value  {{ font-size: 30pt; font-weight: bold; color: {C_TEXT_PRI}; background: transparent; border: none; }}
#card_unit   {{ color: {C_TEXT_SEC}; font-size: 9pt; background: transparent; border: none; }}

/* ═══════════════════════════════════════════
   INPUTS
   ═══════════════════════════════════════════ */
QLineEdit {{
    background-color: {C_BG_INPUT};
    color: {C_TEXT_PRI};
    border: 1px solid {C_BORDER};
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 10pt;
    selection-background-color: {C_ACCENT};
}}
QLineEdit:focus {{
    border: 1px solid {C_ACCENT};
}}
QLineEdit:disabled {{
    color: {C_TEXT_DIM};
    background-color: {C_BG_CARD};
    border: 1px solid {C_BORDER};
}}

/* ═══════════════════════════════════════════
   BUTTONS
   btn_primary  = outlined accent border (like btn_secondary but accent colour)
   btn_secondary = outlined neutral border
   ═══════════════════════════════════════════ */

/* Primary — accent outline button (same shape as secondary, accent colour) */
QPushButton[objectName="btn_primary"] {{
    background-color: transparent;
    color: {C_ACCENT};
    border: 1px solid {C_ACCENT};
    border-radius: 6px;
    padding: 6px 22px;
    font-size: 10pt;
    font-weight: bold;
    min-height: 30px;
}}
QPushButton[objectName="btn_primary"]:hover {{
    background-color: rgba(189,147,249,0.15);
    border: 1px solid #d4b0ff;
    color: #d4b0ff;
}}
QPushButton[objectName="btn_primary"]:pressed {{
    background-color: rgba(189,147,249,0.28);
    border: 1px solid {C_ACCENT};
    color: {C_ACCENT};
}}
QPushButton[objectName="btn_primary"]:disabled {{
    background-color: transparent;
    border: 1px solid {C_BORDER};
    color: {C_TEXT_DIM};
}}

/* Secondary — neutral outline button */
QPushButton[objectName="btn_secondary"] {{
    background-color: transparent;
    color: {C_TEXT_SEC};
    border: 1px solid {C_BORDER_MID};
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 10pt;
    min-height: 30px;
}}
QPushButton[objectName="btn_secondary"]:hover {{
    color: {C_TEXT_PRI};
    border: 1px solid {C_TEXT_SEC};
    background-color: rgba(255,255,255,0.06);
}}
QPushButton[objectName="btn_secondary"]:pressed {{
    background-color: rgba(255,255,255,0.10);
    border: 1px solid {C_TEXT_PRI};
}}

/* ═══════════════════════════════════════════
   SCROLL AREA
   ═══════════════════════════════════════════ */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER_MID};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {C_TEXT_SEC}; }}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; background: none; border: none; }}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{ background: none; }}

/* ═══════════════════════════════════════════
   CONFIG PAGE
   ═══════════════════════════════════════════ */
#pwd_card {{
    background-color: {C_BG_SIDEBAR};
    border: 1px solid {C_BORDER_MID};
    border-radius: 12px;
}}
#pwd_card QLabel {{
    background: transparent;
    border: none;
}}
#pwd_title {{
    font-size: 13pt;
    font-weight: bold;
    color: {C_TEXT_PRI};
    background: transparent;
    border: none;
}}
#pwd_hint {{
    font-size: 9pt;
    color: {C_TEXT_SEC};
    background: transparent;
    border: none;
}}
#pwd_error {{
    font-size: 9pt;
    color: {C_ALARM};
    font-weight: bold;
    background: transparent;
    border: none;
}}
#cfg_form_content {{
    background-color: {C_BG_PANEL};
}}
#cfg_form_content QLabel {{
    background: transparent;
    border: none;
}}
#cfg_section_label {{
    font-size: 10pt;
    font-weight: bold;
    color: {C_ACCENT};
    background: transparent;
    border: none;
}}
#cfg_key_label {{
    font-size: 9pt;
    color: {C_TEXT_SEC};
    background: transparent;
    border: none;
}}
#cfg_action_bar {{
    background-color: {C_BG_SIDEBAR};
    border-top: 1px solid {C_BORDER};
    border-bottom: none;
    border-left: none;
    border-right: none;
}}

/* ═══════════════════════════════════════════
   MESSAGEBOX — replaced by custom _MsgDialog
   in config_page.py; no QSS needed here
   ═══════════════════════════════════════════ */
"""
