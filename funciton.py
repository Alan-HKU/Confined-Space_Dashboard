import logging
import time
import datetime
import json
import os
import configparser
import ctypes
import threading

import psutil
from main import *
from PySide6.QtGui import QScreen
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl

# ─────────────────────────────────────────────
# Constants & config-level defaults
# ─────────────────────────────────────────────
title       = "密閉空間監測系統"
description = "密閉空間監測系統"
ver         = "v1.2b"
configfilename = "config.ini"
Item_display   = 12

# UI style strings
item_font   = "font: 19pt;"
value_font  = "font: 60pt;"
device_font = "font: 14pt;"
bottom_font = "font: 16pt;"
unit_font   = "font: 18pt;"
red         = "background-color: red;"
yellow      = "background-color: yellow;"
green       = "background-color: green;"
trans       = "background: transparent;"

# Runtime state
alarm_active      = False
status_network    = False   # legacy (kept for compatibility)
status_private    = False   # private MQTT connection
status_public     = False   # public MQTT connection
databuffer        = []
battery_record    = {}
_alarm_flash_state = False  # current border flash state


# ─────────────────────────────────────────────
# Config loader
# ─────────────────────────────────────────────
class config:
    def __init__(self):
        self.configfile = configparser.ConfigParser()
        self.configfile.optionxform = str
        self.configfile.read(configfilename, encoding="utf-8")
        conf = {}
        for section in self.configfile:
            for key in self.configfile[section]:
                try:
                    conf[key] = json.loads(self.configfile[section][key])
                except json.JSONDecodeError:
                    conf[key] = self.configfile[section][key]
        globals().update(conf)

    def change_data(self, name, value):
        for section in self.configfile:
            if name in self.configfile[section]:
                self.configfile[section][name] = str(value)
                with open(configfilename, "w", encoding="utf-8") as f:
                    self.configfile.write(f)
                return True
        return False


def get(key):
    return globals()[key]


# ─────────────────────────────────────────────
# Logging init
# ─────────────────────────────────────────────
def logging_init():
    fmt = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt, filename=LogLocation)
    logging.info("Start logging")


# ─────────────────────────────────────────────
# MQTT shared helpers
# ─────────────────────────────────────────────
def set_global_status_network(value):
    # Legacy — kept so old code doesn't break
    global status_network
    status_network = value


def set_mqtt_status(role: str, value: bool):
    """Called by MQTTClient on connect/disconnect. role: 'private' | 'public'"""
    global status_network, status_private, status_public
    if role == "private":
        status_private = value
    else:
        status_public = value
    # overall network = at least one broker connected
    status_network = status_private or status_public


def add_msg_to_buffer(msg):
    global databuffer
    try:
        databuffer.append(json.loads(msg.payload))
    except Exception as exc:
        logging.warning(f"add_msg_to_buffer: {exc}")


from mqtt_client import MQTTClient

def mqtt_client_init(broker, broker_port, topic, role="public"):
    print(f"Initializing MQTT Client -> {broker}:{broker_port}  topic={topic}")
    client = MQTTClient(broker, broker_port, topic, role=role)
    client.start()
    return client


# ─────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────
class data:
    def __init__(self, mqtt_client) -> None:
        self.binded      = None
        self.binded_time = None
        self.value2      = []
        self.get()
        self.send(mqtt_client)

    def send(self, mqtt_client):
        try:
            status = "bind" if self.binded else "unbind"
            for device in self.value2:
                for s in sensor:
                    if s not in device:
                        continue
                    topic = f"sensor/sensor_data/{station_ID}"
                    msg = {
                        "status":        status,
                        "station_id":    station_ID,
                        "location_name": location,
                        "device_id":     device["device_id"],
                        "sensor_type":   s,
                        "value":         device[s],
                    }
                    if not mqtt_client.publish(topic, json.dumps(msg)):
                        break
                    time.sleep(0.02)
        except Exception as exc:
            logging.error(f"data.send: {exc}")

    def get(self):
        time_now = datetime.datetime.now()
        while databuffer:
            msg = databuffer.pop(0)

            if "status" in msg:
                self.binded_time = time_now
                if msg["status"] == "bind":
                    self.binded = True
                elif msg["status"] == "unbind":
                    self.binded = False
                continue

            if "device_id" not in msg:
                logging.warning(f"Message missing device_id: {msg}")
                continue

            msg["time"] = time_now
            idx = next(
                (i for i, d in enumerate(self.value2) if d["device_id"] == msg["device_id"]),
                None,
            )
            if idx is not None:
                self.value2[idx].update(msg)
            else:
                self.value2.append(msg)
                self.value2.sort(key=lambda d: d["device_id"])

    _lastlog = ""

    def log(self):
        try:
            entry = f"Log data:{self.value2}"
            if entry != data._lastlog:
                logging.info(entry)
                data._lastlog = entry
        except Exception as exc:
            logging.error(f"data.log: {exc}")

    def check(self):
        try:
            now = datetime.datetime.now().timestamp()
            for device in self.value2:
                ts = device.get("time", datetime.datetime.now())
                if (now - ts.timestamp()) > ConnectionTimeOut:
                    for k in list(device.keys()):
                        if k not in ("time", "device_id"):
                            device[k] = "-"
        except Exception as exc:
            logging.error(f"data.check: {exc}")


# ─────────────────────────────────────────────
# Status indicator helpers
# ─────────────────────────────────────────────
_CSS_GREEN = ("background-image: url(:/images/images/images/green-dot.png);"
              "background-position:center;background-repeat:no-repeat;")
_CSS_RED   = ("background-image: url(:/images/images/images/red-dot.png);"
              "background-position:center;background-repeat:no-repeat;")

def set_status(window, icon_name: str, active: bool):
    widget = getattr(window.ui, icon_name, None)
    if widget:
        widget.setStyleSheet(_CSS_GREEN if active else _CSS_RED)

def set_status_bind(window, data_obj):
    set_status(window, "icon_2", bool(data_obj.binded))


# ─────────────────────────────────────────────
# Alarm logic
# ─────────────────────────────────────────────
def update_alarm(data_obj):
    global alarm_active
    temp_alarm = False

    for device in data_obj.value2:
        for y, s in enumerate(sensor):
            if s not in device:
                continue
            try:
                val = float(device[s])
                lo2, hi2 = min_max_lv2[y]
                if not (lo2 <= val <= hi2):
                    temp_alarm = True
                    break
            except (ValueError, TypeError):
                pass
        if temp_alarm:
            break

    alarm_active = bool(data_obj.binded and temp_alarm)


# ─────────────────────────────────────────────
# GUI controller
# ─────────────────────────────────────────────
class GUI:
    def __init__(self) -> None:
        self.display_page    = 1
        self.display_list    = None
        self._widgets_cached = False
        self._value_w  = []
        self._unit_w   = []
        self._name_w   = []
        self._device_w = []

        if audio_playing:
            self.alarm_sound = QSoundEffect()
            sound_file = globals().get("alarm_sound_file", "alarm.wav")
            alarm_path = os.path.join(os.path.dirname(__file__), sound_file)
            self.alarm_sound.setSource(QUrl.fromLocalFile(alarm_path))
            self.alarm_sound.setLoopCount(QSoundEffect.Infinite.value)
            self.alarm_sound.setVolume(1.0)
        self._flash_state = False

    def _cache_widgets(self, window):
        if self._widgets_cached:
            return
        ui = window.ui
        self._value_w  = [getattr(ui, f"value_{i}",  None) for i in range(Item_display)]
        self._unit_w   = [getattr(ui, f"unit_{i}",   None) for i in range(Item_display)]
        self._name_w   = [getattr(ui, f"name_{i}",   None) for i in range(Item_display)]
        self._device_w = [getattr(ui, f"device_{i}", None) for i in range(Item_display)]
        self._widgets_cached = True

    def switch_display_device(self, data_obj):
        if not data_obj.value2:
            return
        temp_list = [
            (xi, yi)
            for xi, device in enumerate(data_obj.value2)
            for yi, s in enumerate(sensor)
            if s in device and s != "cam"
        ]
        start = (self.display_page - 1) * Item_display
        self.display_list = temp_list[start : start + Item_display]
        if start + Item_display >= len(temp_list):
            self.display_page = 1
        else:
            self.display_page += 1

    def update(self, window, data_obj):
        global alarm_active, battery_record

        self._cache_widgets(window)
        data_obj.check()

        # Clear all slots
        for i in range(Item_display):
            if self._value_w[i]:
                self._value_w[i].setText("")
                self._value_w[i].setStyleSheet(trans + value_font)
            if self._unit_w[i]:   self._unit_w[i].setText("")
            if self._name_w[i]:   self._name_w[i].setText("")
            if self._device_w[i]: self._device_w[i].setText("")

        # Populate visible slots
        if self.display_list:
            for x, (dev_idx, sen_idx) in enumerate(self.display_list):
                device    = data_obj.value2[dev_idx]
                s         = sensor[sen_idx]
                device_id = device["device_id"]
                raw_val   = device.get(s)
                batt_val  = device.get("Battery", "-")
                battery_record[device_id] = batt_val

                try:
                    float_val = float(raw_val)
                    valid = True
                except (ValueError, TypeError):
                    float_val = None
                    valid = False

                vw = self._value_w[x]
                if vw:
                    if s == "water_level":
                        if raw_val in (None, "", "-", "None"):
                            vw.setText("-")
                            vw.setStyleSheet(red + value_font)
                        elif not valid:
                            vw.setText("Error")
                            vw.setStyleSheet(red + value_font)
                        else:
                            lo2, hi2 = min_max_lv2[sen_idx]
                            if float_val > hi2:
                                vw.setText("過高")
                            elif lo2 <= float_val <= hi2:
                                vw.setText("正常")
                            else:
                                vw.setText("過低")
                    else:
                        vw.setText(str(raw_val))

                    # Colour
                    if not valid:
                        if s != "water_level":
                            vw.setStyleSheet(red + value_font)
                    else:
                        try:
                            lo1, hi1 = min_max_lv1[sen_idx]
                            lo2, hi2 = min_max_lv2[sen_idx]
                            if lo1 <= float_val <= hi1:
                                vw.setStyleSheet(green + value_font)
                            elif lo2 <= float_val <= hi2:
                                vw.setStyleSheet(yellow + value_font)
                            else:
                                vw.setStyleSheet(red + value_font)
                        except Exception:
                            vw.setStyleSheet(red + value_font)

                if self._unit_w[x]:   self._unit_w[x].setText(unit[sen_idx])
                if self._name_w[x]:   self._name_w[x].setText(display_name[sen_idx])
                if self._device_w[x]: self._device_w[x].setText(f"{device_id}號機")

        # Bottom status bar
        now    = datetime.datetime.now()
        batt   = psutil.sensors_battery()
        local  = ""
        if batt:
            icon  = "⚡️🔋" if batt.power_plugged else ("🔋" if batt.percent > 25 else "🪫")
            local = f"{icon}{int(round(batt.percent))}%"

        parts = []
        for did, bval in battery_record.items():
            if str(did) == "0":
                continue
            if isinstance(bval, (int, float)):
                icon = "🔋" if bval > 25 else "🪫"
                parts.append(f"{did}號機 {icon}{bval}%")
            else:
                parts.append(f"{did}號機 {bval}")

        pieces = [now.strftime("%d/%m/%y %H:%M:%S")]
        if local:
            pieces.append(local)
        if parts:
            pieces.append("Data Logger: " + " | ".join(parts))
        window.ui.creditsLabel.setText("  ".join(pieces))

        # Network & bind status icons
        set_status(window, "icon_private", status_private)   # 本地 (private broker)
        set_status(window, "icon",         status_public)    # 網絡 (public broker)
        if data_obj.binded_time is not None:
            elapsed = (datetime.datetime.now() - data_obj.binded_time).total_seconds()
            if elapsed > 10:
                data_obj.binded = False
        set_status(window, "icon_2", bool(data_obj.binded))



        # Alarm audio + border flash
        update_alarm(data_obj)
        if audio_playing:
            if alarm_active and not self.alarm_sound.isPlaying():
                self.alarm_sound.play()
            elif not alarm_active and self.alarm_sound.isPlaying():
                self.alarm_sound.stop()

        # Red border flash on alarm
        # We set the style on the MainWindow (QMainWindow) itself so we don't
        # interfere with bgApp's global QSS background-color rule.
        flash_enabled = globals().get("alarm_border_flash", False)
        if flash_enabled and alarm_active:
            self._flash_state = not self._flash_state
            border_color = "red" if self._flash_state else "transparent"
            window.setStyleSheet(
                f"QMainWindow {{ border: 6px solid {border_color}; }}"
            )
        else:
            if self._flash_state:          # only clear once when alarm ends
                self._flash_state = False
                window.setStyleSheet("")


# ─────────────────────────────────────────────
# GPIO (Windows inpoutx64.dll)
# ─────────────────────────────────────────────
class gpio:
    GPIO_ADDRESSES = {
        "GPIO-H19": 0xFD6D0730,
        "GPIO-H18": 0xFD6D0720,
        "GPIO-H17": 0xFD6D0710,
        "GPIO-H16": 0xFD6D0700,
        "GPIO-H00": 0xFD6D0600,
    }
    OUTPUT_MODE = 0x00800201
    INPUT_MODE  = 0x84000100

    def __init__(self) -> None:
        dll = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inpoutx64.dll")
        self._lib = ctypes.WinDLL(dll)
        self._lib.SetPhysLong.argtypes = [ctypes.c_ulonglong, ctypes.c_uint]
        self._lib.SetPhysLong.restype  = ctypes.c_bool
        self._lib.GetPhysLong.argtypes = [ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_uint)]
        self._lib.GetPhysLong.restype  = ctypes.c_bool

    def set_gpio_value(self, name, val):
        return self._lib.SetPhysLong(self.GPIO_ADDRESSES[name], val)

    def get_gpio_value(self, name):
        pval = ctypes.c_uint()
        ok   = self._lib.GetPhysLong(self.GPIO_ADDRESSES[name], ctypes.byref(pval))
        if not ok:
            return None
        return pval.value != 0x84000102

    def set_input(self, name):
        if not self._lib.SetPhysLong(self.GPIO_ADDRESSES[name], self.INPUT_MODE):
            logging.error(f"Failed to set {name} as input")

    def set_output(self, name):
        if not self._lib.SetPhysLong(self.GPIO_ADDRESSES[name], self.OUTPUT_MODE):
            logging.error(f"Failed to set {name} as output")

    def on(self, name):
        self.set_output(name)
        self.set_gpio_value(name, 0)

    def off(self, name):
        self.set_gpio_value(name, 1)
        self.set_input(name)


# ─────────────────────────────────────────────
# Window initialisation
# ─────────────────────────────────────────────
def window_init(window):
    monitors = QScreen.virtualSiblings(window.screen())
    monitor  = monitors[ScreenDisplayed].availableGeometry()
    window.move(monitor.left(), monitor.top())
    window.showFullScreen()
    window.ui.appMargins.setContentsMargins(0, 0, 0, 0)

    now = datetime.datetime.now()
    window.ui.titleRightInfo.setText(f"{description} - {location} ({station_ID})")
    window.ui.titleRightInfo.setStyleSheet("font: 25pt")
    window.ui.creditsLabel.setText(now.strftime("%H:%M:%S %D"))
    window.ui.status_private.setText("本地")   # private broker
    window.ui.status.setText("網絡")             # public broker
    window.ui.status_2.setText("運行中")
    window.ui.version.setText(ver)

    for w in (window.ui.creditsLabel, window.ui.version,
              window.ui.status_private, window.ui.status, window.ui.status_2):
        w.setStyleSheet(bottom_font)

    ui = window.ui
    style_map = {
        "name_":   item_font,
        "unit_":   unit_font,
        "value_":  value_font,
        "device_": device_font,
    }
    for i in range(Item_display):
        for prefix, style in style_map.items():
            w = getattr(ui, f"{prefix}{i}", None)
            if w:
                w.setText("")
                w.setStyleSheet(style)

    for i in range(min(12, Item_display)):
        for attr, text in (
            (f"name_{i}",  display_name[i] if i < len(display_name) else ""),
            (f"value_{i}", "-"),
            (f"unit_{i}",  unit[i]         if i < len(unit)         else ""),
        ):
            w = getattr(ui, attr, None)
            if w:
                w.setText(text)


# ─────────────────────────────────────────────
# Bootstrap
# ─────────────────────────────────────────────
def all_init():
    global Config
    Config = config()
    logging_init()