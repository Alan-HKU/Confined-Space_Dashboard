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

        self._readings: dict[str, float | None] = {k: None for k in self._sensor_meta}
        self._timestamps: dict[str, datetime | None] = {k: None for k in self._sensor_meta}
        self._valid_ts: dict[str, datetime | None] = {k: None for k in self._sensor_meta}
        self._device_ids: dict[str, str] = {k: "" for k in self._sensor_meta}
        self._device_battery: dict[str, int] = {}
        self._device_signal: dict[str, int] = {}   # signal per device_id

        self._bind: bool = False
        self._prev_bind: bool = False   # track changes for publisher

        # Publisher callback — set externally after Publisher is created
        # Signature: publisher.on_sensor_update(key, meta, value, raw_value,
        #                                        device_id, node_id, bind,
        #                                        battery, signal)
        self._publisher = None

        self._connection_timeout = int(get("ConnectionTimeOut") or 30)
        self._log_path = Path(get("LogLocation") or "Data.log")

    def set_publisher(self, publisher) -> None:
        """Register the upstream Publisher instance."""
        self._publisher = publisher

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

    def _parse(self, msg) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            log.warning("Non-JSON payload on %s", msg.topic)
            return

        if not isinstance(payload, dict):
            return

        # ── Skip our own upstream payloads (heartbeat / bind_event / sensor) ──
        # Public MQTT is publish-only, but if loopback occurs we ignore it.
        msg_type = payload.get("type", "")
        if msg_type in ("heartbeat", "bind_event"):
            log.debug("Ignoring own upstream payload type=%s", msg_type)
            return
        # Heartbeat can also be identified by having 'uptime' field
        if "uptime" in payload and "gateway_id" in payload:
            log.debug("Ignoring own heartbeat payload")
            return

        # ── Bind/unbind control message ──────────────────────────────────────
        bind_status = None
        if "status" in payload and len(payload) <= 2:
            bind_status = str(payload["status"]).strip().lower()
        elif payload.get("type") == "bind_event":
            bind_status = str(payload.get("bind_status", "")).strip().lower()

        if bind_status in ("bind", "unbind"):
            new_bind = (bind_status == "bind")
            with self._lock:
                changed    = (new_bind != self._bind)
                self._bind = new_bind
            log.info("System %s (topic=%s)", "BIND" if new_bind else "UNBIND", msg.topic)
            if changed and self._publisher is not None:
                self._publisher.on_bind_change(new_bind)
            return

        device_id = str(payload.get("device_id", ""))

        # ── Format A: {"sensor_type": "gas_h2s", "value": 3.5, ...} ──────────
        if "sensor_type" in payload:
            raw_key  = payload["sensor_type"]
            key      = self._ALIASES.get(raw_key, raw_key)
            raw_val  = payload.get("value")
            node_id  = int(payload.get("node_id", 0))
            battery  = None
            signal   = None
            for bk in ("battery", "Battery"):
                if bk in payload:
                    try: battery = int(float(payload[bk]))
                    except (TypeError, ValueError): pass
                    break
            for sk in ("signal", "Signal"):
                if sk in payload:
                    try: signal = int(float(payload[sk]))
                    except (TypeError, ValueError): pass
                    break
            if key in self._sensor_meta:
                log.debug("RX [A] sensor=%-20s val=%-10s device=%s", key, raw_val, device_id)
                self._store(key, raw_val, device_id,
                            node_id=node_id, battery=battery, signal=signal)
            else:
                log.debug("Unknown sensor_type: %s (resolved: %s)", raw_key, key)
            return

        # ── Format B: flat dict {"device_id":1, "gas_h2s": "Error", ...} ────
        # skip set: metadata fields AND sensor keys that need alias lookup
        skip = {"device_id", "Battery", "Signal", "battery", "signal",
                "timestamp", "status", "bind_status", "type",
                "site_name", "gateway_id", "node_id",
                # Heartbeat fields (safety net if not caught above)
                "uptime", "cpu_percent", "cpu_temp_c", "memory_mb",
                "sys_memory_pct", "thread_count", "mqtt_tx_count",
                "network", "active_alarms", "alarm_count"}

        battery = None
        signal  = None

        for bk in ("Battery", "battery"):
            if bk in payload and device_id not in ("", "0"):
                try:
                    battery = int(float(payload[bk]))
                    with self._lock:
                        self._device_battery[device_id] = battery
                except (TypeError, ValueError):
                    pass
                break

        for sk in ("Signal", "signal"):
            if sk in payload:
                try:
                    signal = int(float(payload[sk]))
                    with self._lock:
                        self._device_signal[device_id] = signal
                except (TypeError, ValueError):
                    pass
                break

        found = False
        for k, raw_val in payload.items():
            if k in skip:
                continue
            resolved = self._ALIASES.get(k, k)
            if resolved in self._sensor_meta:
                log.debug("RX [B] sensor=%-20s val=%-10s device=%s", resolved, raw_val, device_id)
                self._store(resolved, raw_val, device_id,
                            battery=battery, signal=signal)
                found = True
            else:
                # Try the key itself in sensor_meta (handles gas_pm2.5 in config)
                if k in self._sensor_meta:
                    log.debug("RX [B] sensor=%-20s val=%-10s device=%s", k, raw_val, device_id)
                    self._store(k, raw_val, device_id,
                                battery=battery, signal=signal)
                    found = True
                else:
                    log.debug("Unrecognised key: %s", k)

        if not found:
            log.warning("No sensor keys in payload: %s  (topic=%s)",
                        list(payload.keys()), msg.topic)

    def _store(self, key: str, raw_val, device_id: str,
               node_id: int = 0,
               battery: int | None = None,
               signal:  int | None = None) -> None:
        """Parse raw value, update tracking dicts, and immediately publish upstream."""
        now = datetime.now()

        try:
            value    = float(raw_val)
            is_error = False
        except (TypeError, ValueError):
            value    = None
            is_error = True
            if raw_val not in (None, "Error", "error", "ERROR"):
                log.debug("Non-numeric for %s: %r", key, raw_val)

        with self._lock:
            self._readings[key]    = value
            self._device_ids[key]  = device_id
            self._timestamps[key]  = now
            if not is_error:
                self._valid_ts[key] = now
            bind = self._bind

        if is_error:
            log.debug("Error reading  %-20s  device=%s", key, device_id)
        else:
            log.debug("Updated %-20s = %-10s  device=%s", key, value, device_id)

        # ── Immediately publish to public MQTT ────────────────────────────────
        if self._publisher is not None:
            meta = self._sensor_meta.get(key, {})
            try:
                self._publisher.on_sensor_update(
                    key       = key,
                    meta      = meta,
                    value     = value,
                    raw_value = raw_val,
                    device_id = device_id,
                    node_id   = node_id,
                    bind      = bind,
                    battery   = battery,
                    signal    = signal,
                )
            except Exception as exc:
                log.error("Publisher callback error: %s", exc)

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

    # ── Upstream publish — handled by Publisher ───────────────────────────────

    def send(self, mqtt_client=None) -> None:
        """
        Deprecated: upstream publishing is now handled by Publisher which fires
        immediately on each new reading via the _store() → on_sensor_update()
        callback chain.  This method is kept only so existing QTimer connections
        don't crash; it is a safe no-op.
        """
        pass  # Publisher handles all upstream publishing

    def get_device_signal(self) -> dict[str, int]:
        with self._lock: return dict(self._device_signal)

    def snapshot_for_gui(self) -> list[dict]:
        """
        Return a list of per-sensor dicts for the GUI tick in a single
        lock acquisition.  Avoids 13+ separate lock acquires per frame.

        Each dict: {key, value, device_id, s_state, level, stale, has_ts}
        """
        now     = datetime.now()
        timeout = self._connection_timeout

        with self._lock:
            readings  = dict(self._readings)
            ts_map    = dict(self._timestamps)
            valid_map = dict(self._valid_ts)
            dev_ids   = dict(self._device_ids)
            meta_map  = self._sensor_meta
            bind      = self._bind

        result = []
        for key in meta_map:
            value    = readings.get(key)
            ts       = ts_map.get(key)
            valid_ts = valid_map.get(key)
            dev_id   = dev_ids.get(key, "")
            meta     = meta_map.get(key, {})

            # Compute sensor_state inline
            if ts is None:
                s_state = SENSOR_WAITING
            else:
                age = (now - ts).total_seconds()
                if age > timeout:
                    s_state = SENSOR_OFFLINE
                elif value is not None:
                    s_state = SENSOR_LIVE
                elif valid_ts and (now - valid_ts).total_seconds() <= timeout:
                    s_state = SENSOR_ERROR
                else:
                    s_state = SENSOR_ERROR

            # Compute alarm level inline
            if value is None:
                level = self.NORMAL
            elif not meta.get("alarm_enabled", True):
                lv2_lo, lv2_hi = meta.get("lv2", [0, 9999])
                lv1_lo, lv1_hi = meta.get("lv1", [0, 9999])
                if not (lv2_lo <= value <= lv2_hi): level = self.ALARM
                elif not (lv1_lo <= value <= lv1_hi): level = self.WARN
                else: level = self.NORMAL
            else:
                lv2_lo, lv2_hi = meta.get("lv2", [0, 9999])
                lv1_lo, lv1_hi = meta.get("lv1", [0, 9999])
                if not (lv2_lo <= value <= lv2_hi): level = self.ALARM
                elif not (lv1_lo <= value <= lv1_hi): level = self.WARN
                else: level = self.NORMAL

            result.append({
                "key":      key,
                "value":    value,
                "device_id": dev_id,
                "s_state":  s_state,
                "level":    level,
                "stale":    s_state in (SENSOR_OFFLINE, SENSOR_WAITING),
                "has_ts":   ts is not None,
                "alarm_enabled": meta.get("alarm_enabled", True),
            })

        # Compute any_alarm in same pass:
        # Sound triggers when:
        #   - bind=True (explicit bind message received) OR data is actively arriving
        #   - AND at least one LIVE sensor with alarm_enabled exceeds LV2
        data_arriving = any(r["s_state"] == SENSOR_LIVE for r in result)
        effectively_bound = bind or data_arriving   # treat active data as bound

        any_alarm = effectively_bound and any(
            r["s_state"] == SENSOR_LIVE
            and r["level"] == self.ALARM
            and r["alarm_enabled"]
            for r in result
        )

        # Debug log when alarm condition changes (throttled — logged once per state change)
        alarm_keys = [
            r["key"] for r in result
            if r["s_state"] == SENSOR_LIVE
            and r["level"] == self.ALARM
            and r["alarm_enabled"]
        ]
        if alarm_keys:
            log.debug(
                "Alarm check: bind=%s data_arriving=%s effectively_bound=%s "
                "any_alarm=%s  alarm_keys=%s",
                bind, data_arriving, effectively_bound, any_alarm, alarm_keys
            )

        return result, bind, any_alarm
