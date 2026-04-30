"""
main.py — Entry point for the Confined Space Monitoring System.

Startup order
-------------
1.  CWD → project root
2.  Load config.ini
3.  setup_logging()
4.  QApplication
5.  Private MQTT client  (receive sensor data from local gateway)
6.  Public MQTT client   (upload to server: bind / sensor / heartbeat)
7.  DataModel
8.  Publisher  → wired into DataModel for immediate upstream on new data
9.  MainWindow
10. Qt event loop
"""

import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
os.chdir(PROJECT_ROOT)

from core.config       import load as cfg_load, get
from core.logger_setup import setup_logging

cfg_load("config.ini")

_LEVEL_MAP = {"DEBUG": logging.DEBUG, "INFO": logging.INFO,
              "WARNING": logging.WARNING, "ERROR": logging.ERROR}
_file_level_str = str(get("log_file_level") or "DEBUG").upper()
_file_level = _LEVEL_MAP.get(_file_level_str, logging.DEBUG)

setup_logging(
    log_path      = get("LogLocation")       or "Data.log",
    max_bytes     = int(get("log_max_bytes")     or 5 * 1024 * 1024),
    backup_count  = int(get("log_backup_count")  or 5),
    console_level = logging.DEBUG,
    file_level    = _file_level,
)

log = logging.getLogger(__name__)
log.info("=== 密閉空間監測系統 starting up ===")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui     import QIcon
from PySide6.QtCore    import QTimer

from core.data_model  import DataModel
from core.mqtt_client import make_client
from core.publisher   import Publisher
from ui.main_window   import MainWindow


def _app_icon() -> QIcon:
    p = PROJECT_ROOT / "assets" / "Picture1.png"
    return QIcon(str(p)) if p.exists() else QIcon()


def main():
    os.environ["QT_FONT_DPI"] = str(get("DPI") or "96")

    app = QApplication(sys.argv)
    app.setApplicationName("密閉空間監測系統")
    app.setWindowIcon(_app_icon())

    # ── Private MQTT — receive from local gateway ──────────────────────────────
    private_mqtt = make_client(
        broker = get("private_broker"),
        port   = int(get("private_broker_port") or 1883),
        topic  = get("private_topic"),
        role   = "private",
    )
    log.info("Private MQTT → %s:%s  topic=%s",
             get("private_broker"), get("private_broker_port"), get("private_topic"))

    # ── Public MQTT — upload to server ────────────────────────────────────────
    site_name  = get("location")   or "site_001"
    gateway_id = get("station_ID") or "GW_01"
    pub_prefix = f"cs/{site_name}/{gateway_id}"

    public_mqtt = make_client(
        broker    = get("public_broker"),
        port      = int(get("public_broker_port") or 1883),
        topic     = None,   # publish-only, no subscription to avoid loopback
        role      = "public",
    )
    log.info("Public MQTT  → %s:%s  prefix=%s",
             get("public_broker"), get("public_broker_port"), pub_prefix)

    # ── Data model ────────────────────────────────────────────────────────────
    data = DataModel()

    # ── Publisher — batched sensor upload ────────────────────────────────────
    publisher = Publisher(
        mqtt_client             = public_mqtt,
        site_name               = site_name,
        gateway_id              = gateway_id,
        sensor_upload_interval  = float(get("sensor_upload_interval") or 5),
    )
    data.set_publisher(publisher)
    publisher.start()
    log.info("Publisher started — %s  upload_interval=%.1fs",
             pub_prefix, float(get("sensor_upload_interval") or 5))

    # ── Window ────────────────────────────────────────────────────────────────
    window = MainWindow(data)
    window.showMaximized()
    window._title_bar._maximized = True
    window._title_bar._btn_max.setText("❐")
    window.raise_()
    window.activateWindow()
    log.info("MainWindow shown (maximized)")

    # ── CSV log timer (still useful for local record-keeping) ─────────────────
    t_log = QTimer()
    t_log.timeout.connect(data.log)
    t_log.start(int(get("LoggingTime") or 30000))

    # Note: no send() timer — Publisher fires immediately on each new reading
    # and handles its own heartbeat/bind periodic threads.

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
