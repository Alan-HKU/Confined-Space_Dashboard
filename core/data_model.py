"""
data_model.py — Thread-safe sensor data store and alarm logic.

Bind state:
  Driven by MQTT payload {"status": "bind"} / {"status": "unbind"}
  NOT by stale/timeout — only the explicit status message changes it.

Sensor states per key:
  WAITING  — no MQTT message ever received for this key (ts is None)
  LIVE     — received a valid numeric value within ConnectionTimeOut
  ERROR    — received "Error" within ConnectionTimeOut (sensor fault, not offline)
  OFFLINE  — only Error values received for the full ConnectionTimeOut window
             OR no message at all in ConnectionTimeOut seconds after first seen

Alarm rules:
  - Only triggers when bind=True
  - value=None (Error) does NOT trigger alarm — sensor fault, not a hazard reading
  - Only real numeric values that exceed LV2 trigger alarm
"""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path

from core.config import get, get_sensor

log = logging.getLogger(__name__)


# ── Module-level shared state (MQTT callbacks write, Qt thread reads) ─────────

_status_lock  = threading.Lock()
_mqtt_status  = {"private": False, "public": False}
_msg_buffer: list = []


def set_mqtt_status(role: str, connected: bool) -> None:
    with _status_lock:
        _mqtt_status[role] = connected


def get_mqtt_status(role: str) -> bool:
    with _status_lock:
        return _mqtt_status.get(role, False)


def add_msg_to_buffer(msg) -> None:
    with _status_lock:
        _msg_buffer.append(msg)


# ── Sensor state constants ────────────────────────────────────────────────────

SENSOR_WAITING = "waiting"    # no message ever received
SENSOR_LIVE    = "live"       # has valid numeric reading within timeout
SENSOR_ERROR   = "error"      # latest value is Error, but still within timeout
SENSOR_OFFLINE = "offline"    # no valid numeric value for full timeout window


# ── DataModel ────────────────────────────────────────────────────────────────

class DataModel:

    NORMAL = "normal"
    WARN   = "warn"
    ALARM  = "alarm"

    # Payload key aliases → internal config key
    _ALIASES: dict = {
        "gas_pm2.5": "gas_pm25",
        "pm2.5":     "gas_pm25",
        "pm25":      "gas_pm25",
    }

    def __init__(self, public_mqtt=None):
        self._lock        = threading.Lock()
        self._public_mqtt = public_mqtt
        self._sensor_meta = get_sensor()

        # Latest numeric reading (None if Error or not yet received)
        self._readings: dict[str, float | None] = {k: None for k in self._sensor_meta}

        # Last timestamp when ANY message (including Error) was received
        self._timestamps: dict[str, datetime | None] = {k: None for k in self._sensor_meta}

        # Last timestamp when a VALID NUMERIC value was received
        self._valid_ts: dict[str, datetime | None] = {k: None for k in self._sensor_meta}

        # Device ID last seen per sensor key
        self._device_ids: dict[str, str] = {k: "" for k in self._sensor_meta}

        # Device battery {device_id_str: int_percent}, skip "0"
        self._device_battery: dict[str, int] = {}

        # Bind state — set by {"status": "bind"/"unbind"} message
        self._bind: bool = False

        self._connection_timeout = int(get("ConnectionTimeOut") or 30)
        self._log_path = Path(get("LogLocation") or "Data.log")

    # ── Buffer drain ─────────────────────────────────────────────────────────

    def get(self) -> None:
        """Drain MQTT buffer. Called every GUI tick (and by separate timer)."""
        with _status_lock:
            batch, _msg_buffer[:] = list(_msg_buffer), []
        for msg in batch:
            self._parse(msg)

    # ── Message parsing ───────────────────────────────────────────────────────

    def _parse(self, msg) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            log.warning("Non-JSON payload on %s", msg.topic)
            return

        if not isinstance(payload, dict):
            return

        # ── Bind/unbind control message ──────────────────────────────────────
        if "status" in payload and len(payload) <= 2:
            status = str(payload["status"]).strip().lower()
            if status == "bind":
                with self._lock:
                    self._bind = True
                log.info("System BIND received")
                return
            elif status == "unbind":
                with self._lock:
                    self._bind = False
                log.info("System UNBIND received")
                return

        device_id = str(payload.get("device_id", ""))

        # ── Format A: {"sensor_type": "gas_h2s", "value": 3.5} ──────────────
        if "sensor_type" in payload:
            key      = self._ALIASES.get(payload["sensor_type"], payload["sensor_type"])
            raw_val  = payload.get("value")
            if key in self._sensor_meta:
                self._store(key, raw_val, device_id)
            else:
                log.debug("Unknown sensor_type: %s", payload["sensor_type"])
            return

        # ── Format B: flat dict {"device_id":1, "gas_h2s": "Error", ...} ────
        skip = {"device_id", "Battery", "Signal", "timestamp", "status"}

        if "Battery" in payload and device_id not in ("", "0"):
            try:
                with self._lock:
                    self._device_battery[device_id] = int(float(payload["Battery"]))
            except (TypeError, ValueError):
                pass

        found = False
        for k, raw_val in payload.items():
            if k in skip:
                continue
            resolved = self._ALIASES.get(k, k)
            if resolved in self._sensor_meta:
                self._store(resolved, raw_val, device_id)
                found = True
            else:
                log.debug("Unrecognised flat key: %s", k)

        if not found:
            log.warning("No sensor keys in payload: %s", list(payload.keys()))

    def _store(self, key: str, raw_val, device_id: str) -> None:
        """Parse raw value and update all tracking dicts."""
        now = datetime.now()

        try:
            value = float(raw_val)
            is_error = False
        except (TypeError, ValueError):
            value    = None
            is_error = True
            if raw_val not in (None, "Error", "error", "ERROR"):
                log.debug("Non-numeric for %s: %r", key, raw_val)

        with self._lock:
            self._readings[key]    = value
            self._device_ids[key]  = device_id
            self._timestamps[key]  = now          # always update
            if not is_error:
                self._valid_ts[key] = now          # only update on real value

        if is_error:
            log.debug("Error reading  %-20s  device=%s", key, device_id)
        else:
            log.debug("Updated %-20s = %-10s  device=%s", key, value, device_id)

    # ── Bind state ────────────────────────────────────────────────────────────

    def is_bound(self) -> bool:
        with self._lock:
            return self._bind

    # ── Sensor state ──────────────────────────────────────────────────────────

    def sensor_state(self, key: str) -> str:
        """
        Return one of: SENSOR_WAITING / SENSOR_LIVE / SENSOR_ERROR / SENSOR_OFFLINE

        OFFLINE = timestamp exists (at least one message received) but no valid
                  numeric value within ConnectionTimeOut seconds.
        ERROR   = timestamp fresh BUT value is None (latest was "Error").
        LIVE    = valid_ts fresh AND value is numeric.
        WAITING = no timestamp at all.
        """
        timeout = self._connection_timeout
        now     = datetime.now()

        with self._lock:
            ts       = self._timestamps.get(key)
            valid_ts = self._valid_ts.get(key)
            value    = self._readings.get(key)

        if ts is None:
            return SENSOR_WAITING

        msg_age = (now - ts).total_seconds()

        # No message at all in timeout window → offline
        if msg_age > timeout:
            return SENSOR_OFFLINE

        # Message is fresh — was it a real value or Error?
        if value is not None:
            return SENSOR_LIVE
        else:
            # value is None. Check if we EVER got a valid value within timeout
            if valid_ts is not None and (now - valid_ts).total_seconds() <= timeout:
                # Had a valid value recently — transient error
                return SENSOR_ERROR
            elif valid_ts is None:
                # Never had any valid value — only errors since first message
                # If messages keep coming within timeout, it's ERROR not OFFLINE
                return SENSOR_ERROR
            else:
                # valid_ts exists but stale beyond timeout → offline
                return SENSOR_OFFLINE

    def is_stale(self, key: str) -> bool:
        """Backward-compat: True when sensor_state is OFFLINE or WAITING."""
        return self.sensor_state(key) in (SENSOR_OFFLINE, SENSOR_WAITING)

    def has_timestamp(self, key: str) -> bool:
        with self._lock:
            return self._timestamps.get(key) is not None

    # ── Alarm logic ───────────────────────────────────────────────────────────

    def alarm_level(self, key: str) -> str:
        """
        Return NORMAL / WARN / ALARM.

        Rules:
          - alarm_enabled=False → always NORMAL (border colour still shown but no sound)
          - value is None (Error) → always NORMAL
          - otherwise compare against lv1 / lv2 thresholds
        """
        with self._lock:
            value = self._readings.get(key)
            meta  = self._sensor_meta.get(key, {})

        if not meta.get("alarm_enabled", True):
            # Sensor alarm disabled — still compute visual level for border colour
            # but mark as NORMAL so it never triggers audio alarm
            if value is None:
                return self.NORMAL
            lv1_lo, lv1_hi = meta.get("lv1", [0, 9999])
            lv2_lo, lv2_hi = meta.get("lv2", [0, 9999])
            if not (lv2_lo <= value <= lv2_hi):
                return self.ALARM   # visual only — filtered in any_alarm()
            if not (lv1_lo <= value <= lv1_hi):
                return self.WARN
            return self.NORMAL

        if value is None:
            return self.NORMAL   # Error = not an alarm condition

        lv1_lo, lv1_hi = meta.get("lv1", [0, 9999])
        lv2_lo, lv2_hi = meta.get("lv2", [0, 9999])

        if not (lv2_lo <= value <= lv2_hi):
            return self.ALARM
        if not (lv1_lo <= value <= lv1_hi):
            return self.WARN
        return self.NORMAL

    def any_alarm(self) -> bool:
        """
        True only if at least one LIVE sensor with alarm_enabled=True exceeds LV2.
        Sensors with alarm_enabled=False only show visual colour — never trigger audio.
        """
        for k in self._sensor_meta:
            meta = self._sensor_meta.get(k, {})
            if not meta.get("alarm_enabled", True):
                continue   # skip disabled sensors for audio alarm
            if (self.sensor_state(k) == SENSOR_LIVE
                    and self.alarm_level(k) == self.ALARM):
                return True
        return False

    # ── Accessors ─────────────────────────────────────────────────────────────

    def reading(self, key: str) -> float | None:
        with self._lock: return self._readings.get(key)

    def device_id(self, key: str) -> str:
        with self._lock: return self._device_ids.get(key, "")

    def sensor_keys(self) -> list[str]:
        return list(self._sensor_meta.keys())

    def sensor_meta(self, key: str) -> dict:
        return self._sensor_meta.get(key, {})

    def all_readings_snapshot(self) -> dict:
        with self._lock: return dict(self._readings)

    def get_device_batteries(self) -> dict[str, int]:
        with self._lock: return dict(self._device_battery)

    # ── CSV log ───────────────────────────────────────────────────────────────

    def log(self) -> None:
        snap = self.all_readings_snapshot()
        if all(v is None for v in snap.values()):
            log.debug("CSV log skipped — no data yet")
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not self._log_path.exists():
            header = "timestamp," + ",".join(snap.keys())
            try:
                with open(self._log_path, "w", encoding="utf-8") as f:
                    f.write(header + "\n")
                log.info("CSV log created: %s", self._log_path)
            except OSError as exc:
                log.error("CSV create failed: %s", exc)
                return

        row = now + "," + ",".join("" if v is None else str(v) for v in snap.values())
        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(row + "\n")
            log.debug("CSV: %s", row)
        except OSError as exc:
            log.error("CSV write failed: %s", exc)

    # ── Upstream publish ──────────────────────────────────────────────────────

    def send(self, mqtt_client) -> None:
        if mqtt_client is None:
            return
        snap  = self.all_readings_snapshot()
        topic = get("public_topic") or "Confined_Space_Public/out"
        payload = json.dumps({
            "station": get("station_ID") or "",
            "ts":      datetime.now().isoformat(),
            "data":    {k: v for k, v in snap.items() if v is not None},
        })
        mqtt_client.publish(topic, payload)
