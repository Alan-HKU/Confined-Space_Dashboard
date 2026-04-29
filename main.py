"""
main.py — Entry point for the Confined Space Monitoring System.

Start-up order
--------------
1. Locate project root so relative paths (assets/, config.ini) always resolve
2. setup_logging() — rotating file + coloured console DEBUG output
3. Load config.ini
4. Create QApplication + set window icon
5. Start MQTT clients (background threads)
6. Create DataModel
7. Create MainWindow
8. Start publish timer
9. Enter Qt event loop
"""

import logging
import os
import sys
from pathlib import Path

# ── 0. Ensure CWD is the project directory ───────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
os.chdir(PROJECT_ROOT)

# ── 1. Logging — must happen before any module calls getLogger() ──────────────
from core.config       import load as cfg_load, get
from core.logger_setup import setup_logging

cfg_load("config.ini")   # read log settings before QApplication

setup_logging(
    log_path      = get("LogLocation")       or "Data.log",
    max_bytes     = int(get("log_max_bytes")     or 5 * 1024 * 1024),
    backup_count  = int(get("log_backup_count")  or 5),
    console_level = logging.DEBUG,   # full debug on console
    file_level    = logging.INFO,
)

log = logging.getLogger(__name__)
log.info("=== 密閉空間監測系統 starting up ===")

# ── 2. Qt imports (after logging is set up) ───────────────────────────────────
from PySide6.QtWidgets import QApplication
from PySide6.QtGui     import QIcon
from PySide6.QtCore    import QTimer

from core.data_model  import DataModel
from core.mqtt_client import make_client
from ui.main_window   import MainWindow


def _app_icon() -> QIcon:
    icon_path = PROJECT_ROOT / "assets" / "Picture1.png"
    if icon_path.exists():
        return QIcon(str(icon_path))
    log.warning("App icon not found: %s", icon_path)
    return QIcon()


def main():
    os.environ["QT_FONT_DPI"] = str(get("DPI") or "96")

    app = QApplication(sys.argv)
    app.setApplicationName("密閉空間監測系統")
    app.setWindowIcon(_app_icon())

    # ── MQTT ──────────────────────────────────────────────────────────────────
    private_mqtt = make_client(
        broker = get("private_broker"),
        port   = int(get("private_broker_port") or 1883),
        topic  = get("private_topic"),
        role   = "private",
    )
    log.info("Private MQTT → %s:%s  topic=%s",
             get("private_broker"), get("private_broker_port"), get("private_topic"))

    public_mqtt = make_client(
        broker = get("public_broker"),
        port   = int(get("public_broker_port") or 8086),
        topic  = get("public_topic"),
        role   = "public",
    )
    log.info("Public MQTT  → %s:%s  topic=%s",
             get("public_broker"), get("public_broker_port"), get("public_topic"))

    # ── Data model ────────────────────────────────────────────────────────────
    data = DataModel(public_mqtt=public_mqtt)
    log.debug("DataModel created with %d sensors", len(data.sensor_keys()))

    # ── Window — show maximized and bring to front ────────────────────────────
    window = MainWindow(data)
    window.showMaximized()
    window._title_bar._maximized = True    # sync button icon state
    window._title_bar._btn_max.setText("❐")
    window.raise_()
    window.activateWindow()
    log.info("MainWindow shown (maximized)")

    # ── Upstream publish timer ────────────────────────────────────────────────
    t_send = QTimer()
    t_send.timeout.connect(lambda: data.send(public_mqtt))
    t_send.start(get("MQTTTime") or 10000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
